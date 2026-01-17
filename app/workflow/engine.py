"""
PPK DOCUMENT FACTORY v3.0 - Workflow Engine
============================================
Workflow engine for procurement sequence enforcement
"""

from datetime import datetime, date
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

from ..core.config import WORKFLOW_STAGES, STAGE_CODE_MAP, STAGE_ID_MAP, DOCUMENT_TEMPLATES
from ..core.database import get_db_manager
from ..templates.engine import get_template_engine


class StageStatus(Enum):
    """Status of a workflow stage"""
    PENDING = 'pending'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    SKIPPED = 'skipped'
    LOCKED = 'locked'


@dataclass
class StageInfo:
    """Information about a workflow stage"""
    id: int
    code: str
    name: str
    description: str
    status: StageStatus
    is_current: bool
    is_allowed: bool
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    documents: List[Dict]
    required_documents: List[str]
    message: str


class WorkflowEngine:
    """
    Workflow Engine for managing procurement document sequence
    
    Enforces legal sequence:
    SPESIFIKASI → HPS → KAK → SPK → SPMK → BAHP → BAST → SPP → SSP
    
    Features:
    - Stage status tracking
    - Document generation with workflow validation
    - Batch document generation
    - Stage skipping (with audit trail)
    """
    
    def __init__(self):
        self.db = get_db_manager()
        self.template_engine = get_template_engine()
    
    # =========================================================================
    # WORKFLOW STATUS
    # =========================================================================
    
    def get_workflow_overview(self, paket_id: int) -> Dict:
        """
        Get complete workflow overview for a paket
        
        Returns:
            Dictionary with workflow status, stages, and progress
        """
        paket = self.db.get_paket(paket_id)
        if not paket:
            raise ValueError(f"Paket {paket_id} tidak ditemukan")
        
        stages = self.get_all_stages(paket_id)
        
        # Calculate progress
        completed = sum(1 for s in stages if s.status == StageStatus.COMPLETED)
        total = len(stages)
        progress = (completed / total) * 100 if total > 0 else 0
        
        # Find current stage
        current_stage = next((s for s in stages if s.is_current), None)
        
        # Find next allowed stage
        next_stage = next((s for s in stages 
                         if s.is_allowed and s.status == StageStatus.PENDING), None)
        
        return {
            'paket_id': paket_id,
            'paket_nama': paket['nama'],
            'paket_kode': paket['kode'],
            'status': paket['status'],
            'current_stage': current_stage.code if current_stage else None,
            'next_stage': next_stage.code if next_stage else None,
            'progress': progress,
            'completed_stages': completed,
            'total_stages': total,
            'stages': stages
        }
    
    def get_all_stages(self, paket_id: int) -> List[StageInfo]:
        """Get all stages with their status"""
        workflow_status = self.db.get_workflow_status(paket_id)
        paket = self.db.get_paket(paket_id)
        current_stage = paket.get('current_stage', 'SPESIFIKASI')
        
        # Get all documents for this paket
        all_docs = self.db.get_documents(paket_id)
        docs_by_type = {}
        for doc in all_docs:
            dt = doc['doc_type']
            if dt not in docs_by_type:
                docs_by_type[dt] = []
            docs_by_type[dt].append(doc)
        
        stages = []
        
        for stage_config in WORKFLOW_STAGES:
            # Find status from database
            db_status = next(
                (s for s in workflow_status if s['stage_code'] == stage_config['code']),
                None
            )
            
            status = StageStatus(db_status['status']) if db_status else StageStatus.PENDING
            
            # Check if stage is allowed
            is_allowed, message = self.is_stage_allowed(paket_id, stage_config['code'])
            
            # Get documents for this stage
            stage_docs = []
            for output in stage_config.get('outputs', []):
                if output in docs_by_type:
                    stage_docs.extend(docs_by_type[output])
            
            stages.append(StageInfo(
                id=stage_config['id'],
                code=stage_config['code'],
                name=stage_config['name'],
                description=stage_config['description'],
                status=status,
                is_current=(stage_config['code'] == current_stage),
                is_allowed=is_allowed,
                started_at=db_status['started_at'] if db_status else None,
                completed_at=db_status['completed_at'] if db_status else None,
                documents=stage_docs,
                required_documents=stage_config.get('outputs', []),
                message=message
            ))
        
        return stages
    
    def get_stage_info(self, paket_id: int, stage_code: str) -> Optional[StageInfo]:
        """Get information about a specific stage"""
        stages = self.get_all_stages(paket_id)
        return next((s for s in stages if s.code == stage_code), None)
    
    # =========================================================================
    # STAGE VALIDATION
    # =========================================================================
    
    def is_stage_allowed(self, paket_id: int, stage_code: str) -> Tuple[bool, str]:
        """
        Check if a stage is allowed based on workflow rules
        
        Returns:
            Tuple of (allowed: bool, message: str)
        """
        target_order = STAGE_CODE_MAP.get(stage_code)
        if target_order is None:
            return False, f"Stage {stage_code} tidak dikenal"
        
        workflow_status = self.db.get_workflow_status(paket_id)
        
        # Check all previous stages
        for stage in workflow_status:
            if stage['stage_order'] < target_order:
                if stage['status'] not in ['completed', 'skipped']:
                    prev_stage = STAGE_ID_MAP.get(stage['stage_order'])
                    stage_name = prev_stage['name'] if prev_stage else stage['stage_code']
                    return False, f"Stage '{stage_name}' belum selesai"
        
        # =====================================================================
        # ITEM BARANG VALIDATION
        # =====================================================================
        # Stages that require item_barang to be populated
        stages_requiring_items = ['SPESIFIKASI', 'SURVEY', 'HPS', 'SPP', 'DRPP']
        
        if stage_code in stages_requiring_items:
            items = self.db.get_item_barang(paket_id)
            if not items:
                return False, "Daftar item barang masih kosong. Tambahkan item terlebih dahulu."
        
        # =====================================================================
        # TIM PEMERIKSA VALIDATION
        # =====================================================================
        # Stages that require tim pemeriksa
        stages_requiring_team = ['BAHP']
        
        if stage_code in stages_requiring_team:
            team = self.db.get_tim_pemeriksa(paket_id)
            if len(team) < 2:
                return False, "Tim pemeriksa minimal 2 orang. Atur tim pemeriksa terlebih dahulu."
        
        # Check if already completed
        current_status = next(
            (s for s in workflow_status if s['stage_code'] == stage_code),
            None
        )
        
        if current_status and current_status['status'] == 'completed':
            return True, "Stage sudah selesai (dapat di-generate ulang)"
        
        return True, "Stage dapat diproses"
    
    def validate_document_generation(self, paket_id: int, doc_type: str) -> Tuple[bool, str]:
        """
        Validate if a document can be generated
        
        Returns:
            Tuple of (allowed: bool, message: str)
        """
        # Find which stage this document belongs to
        stage_code = None
        for stage in WORKFLOW_STAGES:
            if doc_type in stage.get('outputs', []):
                stage_code = stage['code']
                break
        
        if not stage_code:
            return False, f"Document type {doc_type} tidak terdaftar dalam workflow"
        
        # Check if stage is allowed
        return self.is_stage_allowed(paket_id, stage_code)
    
    # =========================================================================
    # DOCUMENT GENERATION
    # =========================================================================
    
    def generate_document(self, paket_id: int, doc_type: str,
                          additional_data: Dict = None,
                          force: bool = False) -> Tuple[str, str]:
        """
        Generate document with workflow validation
        
        Args:
            paket_id: ID of paket
            doc_type: Document type
            additional_data: Additional data for template
            force: Force generation even if workflow doesn't allow
        
        Returns:
            Tuple of (filepath, nomor_dokumen)
        """
        # Validate
        if not force:
            allowed, message = self.validate_document_generation(paket_id, doc_type)
            if not allowed:
                raise PermissionError(f"Tidak dapat generate {doc_type}: {message}")
        
        # Find stage for this document
        stage_code = None
        for stage in WORKFLOW_STAGES:
            if doc_type in stage.get('outputs', []):
                stage_code = stage['code']
                break
        
        # Update stage to in_progress
        if stage_code:
            self.db.update_stage_status(paket_id, stage_code, 'in_progress')
        
        # Generate document
        filepath, nomor = self.template_engine.generate_document(
            paket_id, doc_type, additional_data
        )
        
        return filepath, nomor
    
    def generate_stage_documents(self, paket_id: int, stage_code: str,
                                 additional_data: Dict = None,
                                 force: bool = False) -> List[Tuple[str, str, str]]:
        """
        Generate all documents for a stage
        
        Args:
            paket_id: ID of paket
            stage_code: Stage code
            additional_data: Additional data for templates
            force: Force generation
        
        Returns:
            List of tuples (doc_type, filepath, nomor)
        """
        # Validate stage
        if not force:
            allowed, message = self.is_stage_allowed(paket_id, stage_code)
            if not allowed:
                raise PermissionError(f"Stage {stage_code} tidak dapat diproses: {message}")
        
        # Get stage config
        stage_config = STAGE_ID_MAP.get(STAGE_CODE_MAP.get(stage_code))
        if not stage_config:
            raise ValueError(f"Stage {stage_code} tidak dikenal")
        
        # Update stage status
        self.db.update_stage_status(paket_id, stage_code, 'in_progress')
        
        # Generate all documents
        results = []
        all_success = True
        
        for doc_type in stage_config.get('outputs', []):
            try:
                filepath, nomor = self.generate_document(
                    paket_id, doc_type, additional_data, force=True
                )
                results.append((doc_type, filepath, nomor))
            except Exception as e:
                results.append((doc_type, None, f"Error: {str(e)}"))
                all_success = False
        
        # Mark stage as completed if all documents generated
        if all_success and results:
            self.complete_stage(paket_id, stage_code)
        
        return results
    
    def generate_spp_package(self, paket_id: int, 
                            additional_data: Dict = None) -> List[Tuple[str, str, str]]:
        """
        Generate complete SPP package (SPP-LS + DRPP + Kuitansi + SSP)
        
        This is a convenience method for generating all payment documents at once.
        
        Returns:
            List of tuples (doc_type, filepath, nomor)
        """
        # Validate SPP stage
        allowed, message = self.is_stage_allowed(paket_id, 'SPP')
        if not allowed:
            raise PermissionError(f"SPP tidak dapat diproses: {message}")
        
        results = []
        
        # Generate SPP documents
        spp_docs = ['SPP_LS', 'DRPP', 'KUITANSI']
        for doc_type in spp_docs:
            try:
                filepath, nomor = self.generate_document(
                    paket_id, doc_type, additional_data, force=True
                )
                results.append((doc_type, filepath, nomor))
            except Exception as e:
                results.append((doc_type, None, f"Error: {str(e)}"))
        
        # Generate SSP documents
        ssp_docs = ['SSP_PPN', 'SSP_PPH']
        for doc_type in ssp_docs:
            try:
                filepath, nomor = self.generate_document(
                    paket_id, doc_type, additional_data, force=True
                )
                results.append((doc_type, filepath, nomor))
            except Exception as e:
                results.append((doc_type, None, f"Error: {str(e)}"))
        
        # Complete both stages
        self.complete_stage(paket_id, 'SPP')
        self.complete_stage(paket_id, 'SSP')
        
        return results
    
    # =========================================================================
    # STAGE MANAGEMENT
    # =========================================================================
    
    def start_stage(self, paket_id: int, stage_code: str) -> bool:
        """Start a stage (mark as in_progress)"""
        allowed, message = self.is_stage_allowed(paket_id, stage_code)
        if not allowed:
            raise PermissionError(f"Stage {stage_code} tidak dapat dimulai: {message}")
        
        return self.db.update_stage_status(paket_id, stage_code, 'in_progress')
    
    def complete_stage(self, paket_id: int, stage_code: str, 
                       notes: str = None) -> bool:
        """
        Complete a stage and move to next
        
        Args:
            paket_id: ID of paket
            stage_code: Stage code to complete
            notes: Optional notes
        
        Returns:
            Success status
        """
        # Update stage status
        success = self.db.update_stage_status(paket_id, stage_code, 'completed', notes)
        
        if success:
            # Update paket's current stage to next
            current_order = STAGE_CODE_MAP.get(stage_code, 0)
            next_order = current_order + 1
            
            if next_order in STAGE_ID_MAP:
                next_stage = STAGE_ID_MAP[next_order]
                self.db.update_paket(paket_id, {'current_stage': next_stage['code']})
            else:
                # All stages completed
                self.db.update_paket(paket_id, {'status': 'completed'})
        
        return success
    
    def skip_stage(self, paket_id: int, stage_code: str, 
                   reason: str) -> bool:
        """
        Skip a stage (with mandatory reason for audit)
        
        Args:
            paket_id: ID of paket
            stage_code: Stage code to skip
            reason: Reason for skipping (required)
        
        Returns:
            Success status
        """
        if not reason:
            raise ValueError("Alasan wajib diisi untuk skip stage")
        
        # Check if stage can be skipped (some stages cannot be skipped)
        stage_config = STAGE_ID_MAP.get(STAGE_CODE_MAP.get(stage_code))
        if stage_config and stage_config.get('required', True):
            # For now, allow skipping but log warning
            pass
        
        success = self.db.update_stage_status(
            paket_id, stage_code, 'skipped', 
            f"SKIPPED: {reason}"
        )
        
        if success:
            # Move to next stage
            current_order = STAGE_CODE_MAP.get(stage_code, 0)
            next_order = current_order + 1
            
            if next_order in STAGE_ID_MAP:
                next_stage = STAGE_ID_MAP[next_order]
                self.db.update_paket(paket_id, {'current_stage': next_stage['code']})
        
        return success
    
    def reset_stage(self, paket_id: int, stage_code: str) -> bool:
        """Reset stage back to pending"""
        return self.db.update_stage_status(paket_id, stage_code, 'pending')
    
    # =========================================================================
    # QUICK GENERATE HELPERS
    # =========================================================================
    
    def quick_generate_contract_package(self, paket_id: int,
                                        additional_data: Dict = None) -> List[Tuple[str, str, str]]:
        """
        Quick generate all contract-related documents
        SPK → SPMK (if allowed)
        """
        results = []
        
        # Try SPK
        try:
            filepath, nomor = self.generate_document(paket_id, 'SPK', additional_data)
            results.append(('SPK', filepath, nomor))
            self.complete_stage(paket_id, 'SPK')
        except Exception as e:
            results.append(('SPK', None, str(e)))
            return results
        
        # Try SPMK
        try:
            filepath, nomor = self.generate_document(paket_id, 'SPMK', additional_data)
            results.append(('SPMK', filepath, nomor))
            self.complete_stage(paket_id, 'SPMK')
        except Exception as e:
            results.append(('SPMK', None, str(e)))
        
        return results
    
    def quick_generate_completion_package(self, paket_id: int,
                                          additional_data: Dict = None) -> List[Tuple[str, str, str]]:
        """
        Quick generate completion documents
        BAHP → BAST (if allowed)
        """
        results = []
        
        # Try BAHP
        try:
            filepath, nomor = self.generate_document(paket_id, 'BAHP', additional_data)
            results.append(('BAHP', filepath, nomor))
            self.complete_stage(paket_id, 'BAHP')
        except Exception as e:
            results.append(('BAHP', None, str(e)))
            return results
        
        # Try BAST
        try:
            filepath, nomor = self.generate_document(paket_id, 'BAST', additional_data)
            results.append(('BAST', filepath, nomor))
            self.complete_stage(paket_id, 'BAST')
        except Exception as e:
            results.append(('BAST', None, str(e)))
        
        return results


# ============================================================================
# SINGLETON
# ============================================================================

_workflow_engine = None

def get_workflow_engine() -> WorkflowEngine:
    global _workflow_engine
    if _workflow_engine is None:
        _workflow_engine = WorkflowEngine()
    return _workflow_engine


__all__ = ['WorkflowEngine', 'get_workflow_engine', 'StageStatus', 'StageInfo']

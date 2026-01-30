"""
PPK DOCUMENT FACTORY - Workflow Service Layer
==============================================
Centralized service layer for workflow operations.

Features:
- Fase management and transitions
- Deadline management
- Workflow analytics
- Notification management
- Transition validation
- Workflow automation

Author: PPK Document Factory Team
Version: 4.0
"""

from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any, Tuple, Callable
from enum import Enum
import json


# =============================================================================
# CONSTANTS & CONFIGURATION
# =============================================================================

# Fase names
FASE_NAMES = {
    1: "Inisiasi",
    2: "Pencairan UM",
    3: "Pelaksanaan",
    4: "Pertanggungjawaban",
    5: "SPBY & Selesai"
}

# Default SLA per mekanisme (days from start)
DEFAULT_SLA = {
    "UP": 30,
    "TUP": 30,
    "LS": 90,
}

# Required documents per fase per mekanisme
FASE_REQUIREMENTS = {
    "UP": {
        1: ["kak"],  # KAK/TOR
        2: ["kuitansi_um", "spp"],  # Kuitansi UM, SPP
        3: [],  # No specific requirements
        4: ["lpj", "kuitansi_final"],  # LPJ, Kuitansi Final
        5: ["spby", "bast"],  # SPBY, BAST
    },
    "TUP": {
        1: ["kak", "persetujuan"],
        2: ["kuitansi_um"],
        3: [],
        4: ["lpj", "kuitansi_final"],
        5: ["spby", "bast"],
    },
    "LS": {
        1: ["kontrak", "kak"],
        2: [],  # No UM for LS
        3: ["bap", "bast_partial"],
        4: ["invoice", "kuitansi"],
        5: ["bast_final", "spby"],
    },
}

# Allowed fase transitions
ALLOWED_TRANSITIONS = {
    1: [2],      # From 1 can go to 2
    2: [1, 3],   # From 2 can go back to 1 or forward to 3
    3: [2, 4],   # From 3 can go back to 2 or forward to 4
    4: [3, 5],   # From 4 can go back to 3 or forward to 5
    5: [4],      # From 5 can go back to 4
}


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class ValidationResult:
    """Result of a validation check."""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    missing_documents: List[str] = field(default_factory=list)
    missing_fields: List[str] = field(default_factory=list)

    def add_error(self, error: str):
        self.errors.append(error)
        self.is_valid = False

    def add_warning(self, warning: str):
        self.warnings.append(warning)

    def merge(self, other: 'ValidationResult'):
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        self.missing_documents.extend(other.missing_documents)
        self.missing_fields.extend(other.missing_fields)
        if other.errors:
            self.is_valid = False


@dataclass
class WorkflowMetrics:
    """Workflow metrics data."""
    avg_completion_time: timedelta = field(default_factory=lambda: timedelta(days=0))
    avg_time_per_fase: Dict[int, timedelta] = field(default_factory=dict)
    bottleneck_fase: Optional[int] = None
    completion_rate: float = 0.0
    overdue_count: int = 0
    on_track_count: int = 0
    total_count: int = 0
    total_nilai: float = 0.0


@dataclass
class TransitionRequest:
    """Request to transition to a new fase."""
    transaksi_id: str
    from_fase: int
    to_fase: int
    user_id: Optional[str] = None
    force: bool = False
    notes: Optional[str] = None


# =============================================================================
# FASE TRANSITION VALIDATOR
# =============================================================================

class FaseTransitionValidator:
    """
    Validates fase transitions.

    Checks:
    - Transition is allowed
    - Required documents exist
    - Required fields are filled
    - Approval status
    """

    def __init__(self, db_connection=None):
        self.db = db_connection

    def validate_transition(
        self,
        transaksi: Dict[str, Any],
        to_fase: int
    ) -> ValidationResult:
        """
        Validate a fase transition.

        Args:
            transaksi: Transaksi data dictionary
            to_fase: Target fase number

        Returns:
            ValidationResult with errors if invalid
        """
        result = ValidationResult(is_valid=True)

        from_fase = transaksi.get("fase", 1)
        mekanisme = transaksi.get("mekanisme", "UP")

        # Check if transition is allowed
        allowed = ALLOWED_TRANSITIONS.get(from_fase, [])
        if to_fase not in allowed:
            result.add_error(
                f"Transisi dari Fase {from_fase} ke Fase {to_fase} tidak diizinkan. "
                f"Transisi yang diizinkan: {allowed}"
            )
            return result

        # Check required documents for current fase (only for forward transitions)
        if to_fase > from_fase:
            required_docs = self.get_required_documents(mekanisme, from_fase)
            created_docs = transaksi.get("created_documents", [])

            for doc in required_docs:
                if doc not in created_docs:
                    result.missing_documents.append(doc)
                    result.add_error(f"Dokumen '{doc}' belum dibuat")

        # Check required fields
        required_fields = self._get_required_fields(mekanisme, from_fase)
        for field_name, field_label in required_fields.items():
            if not transaksi.get(field_name):
                result.missing_fields.append(field_name)
                result.add_error(f"Field '{field_label}' harus diisi")

        # Check approval status for certain transitions
        if from_fase == 1 and to_fase == 2:
            if not transaksi.get("approved", False):
                result.add_warning("Transaksi belum disetujui")

        # Check if moving forward with overdue status
        deadline = transaksi.get("deadline")
        if deadline and to_fase > from_fase:
            if isinstance(deadline, str):
                deadline = datetime.fromisoformat(deadline).date()
            if deadline < date.today():
                result.add_warning("Transaksi sudah melewati deadline")

        return result

    def get_required_documents(self, mekanisme: str, fase: int) -> List[str]:
        """Get required documents for a fase."""
        mek_reqs = FASE_REQUIREMENTS.get(mekanisme, FASE_REQUIREMENTS["UP"])
        return mek_reqs.get(fase, [])

    def _get_required_fields(self, mekanisme: str, fase: int) -> Dict[str, str]:
        """Get required fields for a fase (field_name -> label)."""
        # Define required fields per fase
        required = {}

        if fase == 1:
            required = {"nama": "Nama Transaksi", "nilai": "Nilai"}

        elif fase == 2:
            if mekanisme in ("UP", "TUP"):
                required = {"um_amount": "Nilai UM"}

        elif fase == 4:
            required = {"realisasi": "Nilai Realisasi"}

        return required


# =============================================================================
# WORKFLOW SERVICE
# =============================================================================

class WorkflowService:
    """
    Centralized service for workflow operations.

    Provides methods for:
    - Fase management
    - Deadline management
    - Analytics
    - Notifications
    """

    def __init__(self, db_connection=None, event_logger=None):
        """
        Initialize workflow service.

        Args:
            db_connection: Database connection
            event_logger: WorkflowEventLogger instance for logging events
        """
        self.db = db_connection
        self.event_logger = event_logger
        self.validator = FaseTransitionValidator(db_connection)

        # Callbacks for notifications
        self._notification_callbacks: List[Callable] = []

    # -------------------------------------------------------------------------
    # Fase Management
    # -------------------------------------------------------------------------

    def get_current_fase(self, transaksi_id: str) -> int:
        """
        Get current fase of a transaksi.

        Args:
            transaksi_id: Transaksi ID

        Returns:
            Current fase number (1-5)
        """
        if self.db:
            # Query database
            transaksi = self._get_transaksi(transaksi_id)
            if transaksi:
                return transaksi.get("fase", 1)
        return 1

    def can_move_to_fase(
        self,
        transaksi_id: str,
        target_fase: int
    ) -> Tuple[bool, str]:
        """
        Check if transaksi can move to target fase.

        Args:
            transaksi_id: Transaksi ID
            target_fase: Target fase number

        Returns:
            Tuple of (can_move, reason)
        """
        transaksi = self._get_transaksi(transaksi_id)
        if not transaksi:
            return False, "Transaksi tidak ditemukan"

        result = self.validator.validate_transition(transaksi, target_fase)

        if result.is_valid:
            return True, "OK"
        else:
            return False, "; ".join(result.errors)

    def move_to_fase(
        self,
        transaksi_id: str,
        target_fase: int,
        user_id: Optional[str] = None,
        notes: Optional[str] = None,
        force: bool = False
    ) -> Tuple[bool, str]:
        """
        Move transaksi to a new fase.

        Args:
            transaksi_id: Transaksi ID
            target_fase: Target fase number
            user_id: User performing the action
            notes: Optional notes
            force: Force move even with warnings

        Returns:
            Tuple of (success, message)
        """
        transaksi = self._get_transaksi(transaksi_id)
        if not transaksi:
            return False, "Transaksi tidak ditemukan"

        from_fase = transaksi.get("fase", 1)

        # Validate transition
        if not force:
            result = self.validator.validate_transition(transaksi, target_fase)
            if not result.is_valid:
                return False, "; ".join(result.errors)

        # Perform update
        if self.db:
            try:
                self._update_transaksi_fase(transaksi_id, target_fase)

                # Log event
                if self.event_logger:
                    self.event_logger.log_fase_changed(
                        transaksi_id=transaksi_id,
                        from_fase=from_fase,
                        to_fase=target_fase,
                        user=user_id
                    )

                # Update last activity
                self._update_last_activity(transaksi_id)

                return True, f"Berhasil pindah ke Fase {target_fase}"

            except Exception as e:
                return False, f"Error: {str(e)}"

        return True, f"Berhasil pindah ke Fase {target_fase}"

    def get_fase_requirements(self, mekanisme: str, fase: int) -> List[str]:
        """
        Get required documents for a fase.

        Args:
            mekanisme: Payment mechanism (UP/TUP/LS)
            fase: Fase number

        Returns:
            List of required document types
        """
        return self.validator.get_required_documents(mekanisme, fase)

    def check_fase_completion(
        self,
        transaksi_id: str,
        fase: int
    ) -> Dict[str, Any]:
        """
        Check completion status of a fase.

        Args:
            transaksi_id: Transaksi ID
            fase: Fase number to check

        Returns:
            Dict with completion status and missing items
        """
        transaksi = self._get_transaksi(transaksi_id)
        if not transaksi:
            return {"complete": False, "error": "Transaksi tidak ditemukan"}

        mekanisme = transaksi.get("mekanisme", "UP")
        created_docs = transaksi.get("created_documents", [])
        required_docs = self.get_fase_requirements(mekanisme, fase)

        missing_docs = [d for d in required_docs if d not in created_docs]

        return {
            "complete": len(missing_docs) == 0,
            "required_documents": required_docs,
            "created_documents": created_docs,
            "missing_documents": missing_docs,
            "completion_percentage": (
                (len(created_docs) / len(required_docs) * 100)
                if required_docs else 100
            )
        }

    # -------------------------------------------------------------------------
    # Deadline Management
    # -------------------------------------------------------------------------

    def calculate_deadline(self, transaksi: Dict[str, Any]) -> Optional[date]:
        """
        Calculate deadline for a transaksi.

        Args:
            transaksi: Transaksi data dictionary

        Returns:
            Calculated deadline date
        """
        # Check for custom deadline
        if transaksi.get("deadline"):
            dl = transaksi["deadline"]
            if isinstance(dl, str):
                return datetime.fromisoformat(dl).date()
            elif isinstance(dl, datetime):
                return dl.date()
            elif isinstance(dl, date):
                return dl

        mekanisme = transaksi.get("mekanisme", "UP")
        sla_days = transaksi.get("sla_days") or DEFAULT_SLA.get(mekanisme, 30)

        # Get start date based on mekanisme
        start_date = None
        if mekanisme == "UP":
            start_date = transaksi.get("um_date") or transaksi.get("created_at")
        elif mekanisme == "TUP":
            start_date = transaksi.get("approval_date") or transaksi.get("created_at")
        else:  # LS
            start_date = transaksi.get("contract_date") or transaksi.get("created_at")

        if start_date:
            if isinstance(start_date, str):
                start_date = datetime.fromisoformat(start_date).date()
            elif isinstance(start_date, datetime):
                start_date = start_date.date()

            return start_date + timedelta(days=sla_days)

        return None

    def get_deadline_status(self, transaksi_id: str) -> str:
        """
        Get deadline status of a transaksi.

        Args:
            transaksi_id: Transaksi ID

        Returns:
            Status string: on_track, warning, due_soon, overdue
        """
        transaksi = self._get_transaksi(transaksi_id)
        if not transaksi:
            return "unknown"

        deadline = self.calculate_deadline(transaksi)
        if not deadline:
            return "on_track"

        days_remaining = (deadline - date.today()).days

        if days_remaining < 0:
            return "overdue"
        elif days_remaining <= 3:
            return "due_soon"
        elif days_remaining <= 7:
            return "warning"
        return "on_track"

    def update_deadline(
        self,
        transaksi_id: str,
        new_deadline: date,
        user_id: Optional[str] = None,
        reason: Optional[str] = None
    ) -> bool:
        """
        Update deadline for a transaksi.

        Args:
            transaksi_id: Transaksi ID
            new_deadline: New deadline date
            user_id: User performing the action
            reason: Reason for change

        Returns:
            Success status
        """
        if self.db:
            try:
                # Update database
                old_deadline = self.calculate_deadline(
                    self._get_transaksi(transaksi_id) or {}
                )

                self._update_transaksi_deadline(transaksi_id, new_deadline)

                # Log event
                if self.event_logger:
                    self.event_logger.log_event(
                        transaksi_id=transaksi_id,
                        event_type="deadline_changed",
                        description=f"Deadline diubah ke {new_deadline.strftime('%d/%m/%Y')}",
                        user=user_id,
                        metadata={
                            "old_deadline": str(old_deadline) if old_deadline else None,
                            "new_deadline": str(new_deadline),
                            "reason": reason
                        }
                    )

                return True
            except Exception:
                return False
        return True

    def get_overdue_transaksi(self) -> List[Dict[str, Any]]:
        """
        Get all overdue transaksi.

        Returns:
            List of overdue transaksi dictionaries
        """
        all_transaksi = self._get_all_active_transaksi()
        overdue = []

        for t in all_transaksi:
            deadline = self.calculate_deadline(t)
            if deadline and deadline < date.today():
                t["days_overdue"] = (date.today() - deadline).days
                overdue.append(t)

        return sorted(overdue, key=lambda x: x.get("days_overdue", 0), reverse=True)

    # -------------------------------------------------------------------------
    # Analytics
    # -------------------------------------------------------------------------

    def get_workflow_metrics(
        self,
        mekanisme: Optional[str] = None,
        period: Optional[Tuple[date, date]] = None
    ) -> WorkflowMetrics:
        """
        Get workflow metrics.

        Args:
            mekanisme: Filter by mekanisme (optional)
            period: Tuple of (start_date, end_date) for filtering

        Returns:
            WorkflowMetrics instance
        """
        transaksi_list = self._get_all_transaksi()

        # Filter by mekanisme
        if mekanisme:
            transaksi_list = [t for t in transaksi_list if t.get("mekanisme") == mekanisme]

        # Filter by period
        if period:
            start, end = period
            filtered = []
            for t in transaksi_list:
                created = t.get("created_at")
                if created:
                    if isinstance(created, str):
                        created = datetime.fromisoformat(created).date()
                    elif isinstance(created, datetime):
                        created = created.date()
                    if start <= created <= end:
                        filtered.append(t)
            transaksi_list = filtered

        if not transaksi_list:
            return WorkflowMetrics()

        # Calculate metrics
        total_count = len(transaksi_list)
        completed_count = sum(1 for t in transaksi_list if t.get("status") == "Selesai")
        total_nilai = sum(t.get("nilai", 0) for t in transaksi_list)

        # Overdue count
        overdue_count = 0
        for t in transaksi_list:
            if t.get("status") != "Selesai":
                deadline = self.calculate_deadline(t)
                if deadline and deadline < date.today():
                    overdue_count += 1

        # Completion rate
        completion_rate = (completed_count / total_count * 100) if total_count > 0 else 0

        # Average completion time
        completion_times = []
        for t in transaksi_list:
            if t.get("status") == "Selesai":
                created = t.get("created_at")
                completed = t.get("completed_at")
                if created and completed:
                    if isinstance(created, str):
                        created = datetime.fromisoformat(created)
                    if isinstance(completed, str):
                        completed = datetime.fromisoformat(completed)
                    completion_times.append(completed - created)

        avg_completion = timedelta(days=0)
        if completion_times:
            total_seconds = sum(t.total_seconds() for t in completion_times)
            avg_completion = timedelta(seconds=total_seconds / len(completion_times))

        # Time per fase
        fase_times: Dict[int, List[float]] = {i: [] for i in range(1, 6)}
        for t in transaksi_list:
            fase_history = t.get("fase_history", [])
            for entry in fase_history:
                fase = entry.get("fase")
                duration = entry.get("duration_days", 0)
                if fase and fase in fase_times:
                    fase_times[fase].append(duration)

        avg_time_per_fase = {}
        for fase, times in fase_times.items():
            if times:
                avg_time_per_fase[fase] = timedelta(days=sum(times) / len(times))
            else:
                avg_time_per_fase[fase] = timedelta(days=0)

        # Find bottleneck
        bottleneck = None
        max_time = timedelta(days=0)
        for fase, time in avg_time_per_fase.items():
            if time > max_time:
                max_time = time
                bottleneck = fase

        return WorkflowMetrics(
            avg_completion_time=avg_completion,
            avg_time_per_fase=avg_time_per_fase,
            bottleneck_fase=bottleneck,
            completion_rate=completion_rate,
            overdue_count=overdue_count,
            on_track_count=total_count - overdue_count - completed_count,
            total_count=total_count,
            total_nilai=total_nilai
        )

    def get_bottleneck_analysis(self) -> Dict[str, Any]:
        """
        Analyze workflow bottlenecks.

        Returns:
            Dict with bottleneck analysis
        """
        metrics = self.get_workflow_metrics()

        # Count transaksi per fase
        transaksi_list = self._get_all_active_transaksi()
        fase_counts = {i: 0 for i in range(1, 6)}
        for t in transaksi_list:
            fase = t.get("fase", 1)
            fase_counts[fase] = fase_counts.get(fase, 0) + 1

        # Find fase with most transaksi
        most_crowded = max(fase_counts.items(), key=lambda x: x[1])

        return {
            "bottleneck_fase": metrics.bottleneck_fase,
            "bottleneck_avg_time": metrics.avg_time_per_fase.get(metrics.bottleneck_fase),
            "fase_counts": fase_counts,
            "most_crowded_fase": most_crowded[0],
            "most_crowded_count": most_crowded[1],
            "avg_time_per_fase": {
                k: v.days + v.seconds / 86400
                for k, v in metrics.avg_time_per_fase.items()
            }
        }

    def get_completion_forecast(self, transaksi_id: str) -> Optional[date]:
        """
        Forecast completion date for a transaksi.

        Args:
            transaksi_id: Transaksi ID

        Returns:
            Forecasted completion date
        """
        transaksi = self._get_transaksi(transaksi_id)
        if not transaksi:
            return None

        current_fase = transaksi.get("fase", 1)
        mekanisme = transaksi.get("mekanisme", "UP")

        # Get average time per fase
        metrics = self.get_workflow_metrics(mekanisme=mekanisme)

        # Calculate remaining time
        remaining_days = 0
        for fase in range(current_fase, 6):
            fase_time = metrics.avg_time_per_fase.get(fase, timedelta(days=3))
            remaining_days += fase_time.days

        return date.today() + timedelta(days=remaining_days)

    # -------------------------------------------------------------------------
    # Notifications
    # -------------------------------------------------------------------------

    def check_and_create_notifications(self) -> List[Dict[str, Any]]:
        """
        Check for conditions that require notifications.

        Returns:
            List of created notifications
        """
        notifications = []

        all_transaksi = self._get_all_active_transaksi()

        for t in all_transaksi:
            transaksi_id = str(t.get("id", ""))
            nomor = t.get("nomor", "")

            # Check deadline
            deadline = self.calculate_deadline(t)
            if deadline:
                days_remaining = (deadline - date.today()).days

                if days_remaining < 0:
                    notifications.append({
                        "type": "deadline_overdue",
                        "title": f"{nomor} melewati deadline",
                        "message": f"Transaksi sudah terlambat {abs(days_remaining)} hari",
                        "transaksi_id": transaksi_id,
                        "priority": "urgent"
                    })
                elif days_remaining <= 3:
                    notifications.append({
                        "type": "deadline_urgent",
                        "title": f"{nomor} deadline dalam {days_remaining} hari",
                        "message": "Segera selesaikan transaksi ini",
                        "transaksi_id": transaksi_id,
                        "priority": "high"
                    })
                elif days_remaining <= 7:
                    notifications.append({
                        "type": "deadline_warning",
                        "title": f"{nomor} deadline dalam {days_remaining} hari",
                        "message": "Perhatikan deadline transaksi",
                        "transaksi_id": transaksi_id,
                        "priority": "medium"
                    })

            # Check stuck transaksi
            fase_start = t.get("fase_start_date")
            if fase_start:
                if isinstance(fase_start, str):
                    fase_start = datetime.fromisoformat(fase_start).date()
                elif isinstance(fase_start, datetime):
                    fase_start = fase_start.date()

                days_in_fase = (date.today() - fase_start).days
                if days_in_fase >= 7:
                    fase = t.get("fase", 1)
                    notifications.append({
                        "type": "transaksi_stuck",
                        "title": f"{nomor} stuck di Fase {fase}",
                        "message": f"Transaksi sudah {days_in_fase} hari di fase yang sama",
                        "transaksi_id": transaksi_id,
                        "priority": "high"
                    })

        return notifications

    def get_unread_notifications(self) -> List[Dict[str, Any]]:
        """Get unread notifications from database."""
        if self.db:
            # Query database for unread notifications
            pass
        return []

    def dismiss_notification(self, notification_id: str) -> bool:
        """Dismiss/mark notification as read."""
        if self.db:
            # Update database
            pass
        return True

    def register_notification_callback(self, callback: Callable):
        """Register a callback for new notifications."""
        self._notification_callbacks.append(callback)

    # -------------------------------------------------------------------------
    # Private Database Methods
    # -------------------------------------------------------------------------

    def _get_transaksi(self, transaksi_id: str) -> Optional[Dict[str, Any]]:
        """Get transaksi by ID from database."""
        if self.db:
            # Query database
            pass
        return None

    def _get_all_transaksi(self) -> List[Dict[str, Any]]:
        """Get all transaksi from database."""
        if self.db:
            # Query database
            pass
        return []

    def _get_all_active_transaksi(self) -> List[Dict[str, Any]]:
        """Get all active (non-completed) transaksi."""
        all_transaksi = self._get_all_transaksi()
        return [t for t in all_transaksi if t.get("status") != "Selesai"]

    def _update_transaksi_fase(self, transaksi_id: str, fase: int):
        """Update transaksi fase in database."""
        if self.db:
            # Update database
            pass

    def _update_transaksi_deadline(self, transaksi_id: str, deadline: date):
        """Update transaksi deadline in database."""
        if self.db:
            # Update database
            pass

    def _update_last_activity(self, transaksi_id: str):
        """Update last activity timestamp."""
        if self.db:
            # Update database
            pass


# =============================================================================
# WORKFLOW AUTOMATION
# =============================================================================

class WorkflowAutomation:
    """
    Automated workflow actions.

    Features:
    - Auto-advance to next fase when requirements met
    - Auto-create notifications for issues
    - Auto-update deadline status
    """

    def __init__(self, workflow_service: WorkflowService):
        self.service = workflow_service

    def run_automation(self) -> Dict[str, Any]:
        """
        Run all automation checks.

        Returns:
            Dict with automation results
        """
        results = {
            "auto_advanced": [],
            "notifications_created": [],
            "errors": []
        }

        # Check for auto-advance opportunities
        transaksi_list = self.service._get_all_active_transaksi()

        for t in transaksi_list:
            transaksi_id = str(t.get("id", ""))
            current_fase = t.get("fase", 1)

            if current_fase < 5:
                # Check if can auto-advance
                completion = self.service.check_fase_completion(transaksi_id, current_fase)
                if completion.get("complete", False):
                    next_fase = current_fase + 1
                    can_move, reason = self.service.can_move_to_fase(transaksi_id, next_fase)

                    if can_move:
                        success, msg = self.service.move_to_fase(
                            transaksi_id,
                            next_fase,
                            user_id="system",
                            notes="Auto-advance: semua requirement terpenuhi"
                        )
                        if success:
                            results["auto_advanced"].append({
                                "transaksi_id": transaksi_id,
                                "from_fase": current_fase,
                                "to_fase": next_fase
                            })

        # Create notifications
        notifications = self.service.check_and_create_notifications()
        results["notifications_created"] = notifications

        return results

    def schedule_run(self, interval_minutes: int = 30):
        """
        Schedule automation to run periodically.

        Note: This should be called from QTimer in the UI layer.
        """
        pass


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

def create_workflow_service(
    db_connection=None,
    event_logger=None
) -> WorkflowService:
    """
    Create a WorkflowService instance.

    Args:
        db_connection: Database connection
        event_logger: Event logger instance

    Returns:
        Configured WorkflowService
    """
    return WorkflowService(
        db_connection=db_connection,
        event_logger=event_logger
    )


def create_fase_validator(db_connection=None) -> FaseTransitionValidator:
    """
    Create a FaseTransitionValidator instance.

    Args:
        db_connection: Database connection

    Returns:
        Configured FaseTransitionValidator
    """
    return FaseTransitionValidator(db_connection=db_connection)

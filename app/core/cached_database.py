"""
PPK Document Factory - Cached Database Manager
==============================================
Wrapper for DatabaseManager with caching support.

This module provides a CachedDatabaseManager that wraps the existing
DatabaseManager and adds caching for frequently accessed data.

Cache TTL Values:
----------------
- satker:active       - 3600s (1 hour)
- pegawai:all         - 1800s (30 minutes)
- pegawai:{id}        - 1800s (30 minutes)
- penyedia:all        - 1800s (30 minutes)
- penyedia:{id}       - 1800s (30 minutes)
- paket:list          - 60s (1 minute)
- paket:{id}          - 300s (5 minutes)
- stats               - 60s (1 minute)
- saldo:up            - 30s (30 seconds)

Invalidation Rules:
------------------
- create_paket() -> invalidate "paket:*", "stats:*"
- update_paket() -> invalidate "paket:{id}", "paket:list:*", "stats:*"
- delete_paket() -> invalidate "paket:*", "stats:*"
- update_satker() -> invalidate "satker:*"
- create/update/delete_pegawai() -> invalidate "pegawai:*"
- create/update/delete_penyedia() -> invalidate "penyedia:*"

Example Usage:
-------------
```python
from app.core.cached_database import CachedDatabaseManager

db = CachedDatabaseManager()

# Cached read operations
satker = db.get_satker()  # Cached for 1 hour
pegawai_list = db.get_all_pegawai()  # Cached for 30 minutes
paket_list = db.get_paket_list()  # Cached for 1 minute

# Write operations automatically invalidate cache
db.create_paket(data)  # Invalidates paket:*, stats:*

# Manual cache control
db.invalidate_cache("paket:*")  # Invalidate specific pattern
db.clear_cache()  # Clear all cache
stats = db.cache_stats  # Get cache statistics
```
"""

from typing import Any, Dict, List, Optional
import logging
import hashlib
import json

from .database import DatabaseManager, get_db_manager
from .cache import DataCache, cached, cache_invalidate

logger = logging.getLogger(__name__)


# =============================================================================
# CACHE TTL CONSTANTS
# =============================================================================

# TTL values in seconds
TTL_SATKER = 3600       # 1 hour
TTL_PEGAWAI = 1800      # 30 minutes
TTL_PENYEDIA = 1800     # 30 minutes
TTL_PAKET_DETAIL = 300  # 5 minutes
TTL_PAKET_LIST = 60     # 1 minute
TTL_STATS = 60          # 1 minute
TTL_SALDO = 30          # 30 seconds
TTL_TEMPLATE = 3600     # 1 hour
TTL_WORKFLOW = 60       # 1 minute


# =============================================================================
# CACHED DATABASE MANAGER
# =============================================================================


class CachedDatabaseManager:
    """
    DatabaseManager wrapper with caching support.

    Provides cached versions of read operations and automatic
    cache invalidation on write operations.

    All methods delegate to the underlying DatabaseManager while
    managing cache for improved performance.
    """

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        """
        Initialize CachedDatabaseManager.

        Args:
            db_manager: Existing DatabaseManager instance (creates new if None)
        """
        self._db = db_manager or get_db_manager()
        self._cache = DataCache()
        logger.debug("CachedDatabaseManager initialized")

    @property
    def db(self) -> DatabaseManager:
        """Get underlying database manager."""
        return self._db

    @property
    def cache(self) -> DataCache:
        """Get cache instance."""
        return self._cache

    @property
    def cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return self._cache.stats.to_dict()

    def clear_cache(self) -> None:
        """Clear all cached data."""
        self._cache.clear()

    def invalidate_cache(self, pattern: str) -> int:
        """
        Invalidate cache entries matching pattern.

        Args:
            pattern: Glob pattern (e.g., "paket:*")

        Returns:
            Number of entries invalidated
        """
        return self._cache.invalidate_pattern(pattern)

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    def _make_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from prefix and arguments."""
        if not args and not kwargs:
            return prefix

        # Create hash of arguments
        data = json.dumps({"a": args, "k": kwargs}, sort_keys=True, default=str)
        data_hash = hashlib.md5(data.encode()).hexdigest()[:8]
        return f"{prefix}:{data_hash}"

    # =========================================================================
    # SATKER OPERATIONS (cached)
    # =========================================================================

    def get_satker(self) -> Dict:
        """Get satker data (cached for 1 hour)."""
        key = "satker:active"

        def fetch():
            return self._db.get_satker()

        return self._cache.get_or_set(key, fetch, ttl=TTL_SATKER)

    def get_satker_pejabat(self) -> Dict:
        """Get satker pejabat data (cached for 1 hour)."""
        key = "satker:pejabat"

        def fetch():
            return self._db.get_satker_pejabat()

        return self._cache.get_or_set(key, fetch, ttl=TTL_SATKER)

    def update_satker(self, data: Dict) -> bool:
        """Update satker and invalidate cache."""
        result = self._db.update_satker(data)
        self._cache.invalidate_pattern("satker:*")
        logger.debug("Satker cache invalidated")
        return result

    def update_satker_pejabat(
        self,
        kpa_id: int = None,
        ppk_id: int = None,
        ppspm_id: int = None,
        bendahara_id: int = None
    ) -> bool:
        """Update satker pejabat and invalidate cache."""
        result = self._db.update_satker_pejabat(
            kpa_id, ppk_id, ppspm_id, bendahara_id
        )
        self._cache.invalidate_pattern("satker:*")
        return result

    # =========================================================================
    # PEGAWAI OPERATIONS (cached)
    # =========================================================================

    def get_all_pegawai(
        self,
        active_only: bool = True,
        search: str = None
    ) -> List[Dict]:
        """Get all pegawai (cached for 30 minutes)."""
        key = self._make_key("pegawai:list", active_only=active_only, search=search)

        def fetch():
            return self._db.get_all_pegawai(active_only=active_only, search=search)

        return self._cache.get_or_set(key, fetch, ttl=TTL_PEGAWAI)

    def get_pegawai_list(self, role: str = None) -> List[Dict]:
        """Get pegawai list by role (cached for 30 minutes)."""
        key = self._make_key("pegawai:role", role=role)

        def fetch():
            return self._db.get_pegawai_list(role=role)

        return self._cache.get_or_set(key, fetch, ttl=TTL_PEGAWAI)

    def get_pegawai(self, pegawai_id: int) -> Optional[Dict]:
        """Get single pegawai (cached for 30 minutes)."""
        key = f"pegawai:{pegawai_id}"

        def fetch():
            return self._db.get_pegawai(pegawai_id)

        return self._cache.get_or_set(key, fetch, ttl=TTL_PEGAWAI)

    def get_pegawai_by_nip(self, nip: str) -> Optional[Dict]:
        """Get pegawai by NIP (cached)."""
        key = f"pegawai:nip:{nip}"

        def fetch():
            return self._db.get_pegawai_by_nip(nip)

        return self._cache.get_or_set(key, fetch, ttl=TTL_PEGAWAI)

    def create_pegawai(self, data: Dict) -> int:
        """Create pegawai and invalidate cache."""
        result = self._db.create_pegawai(data)
        self._cache.invalidate_pattern("pegawai:*")
        logger.debug("Pegawai cache invalidated")
        return result

    def update_pegawai(self, pegawai_id: int, data: Dict) -> bool:
        """Update pegawai and invalidate cache."""
        result = self._db.update_pegawai(pegawai_id, data)
        self._cache.delete(f"pegawai:{pegawai_id}")
        self._cache.invalidate_pattern("pegawai:list:*")
        self._cache.invalidate_pattern("pegawai:role:*")
        return result

    def delete_pegawai(self, pegawai_id: int) -> bool:
        """Delete pegawai and invalidate cache."""
        result = self._db.delete_pegawai(pegawai_id)
        self._cache.invalidate_pattern("pegawai:*")
        return result

    # =========================================================================
    # PENYEDIA OPERATIONS (cached)
    # =========================================================================

    def get_penyedia_list(self) -> List[Dict]:
        """Get all penyedia (cached for 30 minutes)."""
        key = "penyedia:all"

        def fetch():
            return self._db.get_penyedia_list()

        return self._cache.get_or_set(key, fetch, ttl=TTL_PENYEDIA)

    def get_penyedia(self, penyedia_id: int) -> Optional[Dict]:
        """Get single penyedia (cached for 30 minutes)."""
        key = f"penyedia:{penyedia_id}"

        def fetch():
            return self._db.get_penyedia(penyedia_id)

        return self._cache.get_or_set(key, fetch, ttl=TTL_PENYEDIA)

    def get_penyedia_by_npwp(self, npwp: str) -> Optional[Dict]:
        """Get penyedia by NPWP (cached)."""
        key = f"penyedia:npwp:{npwp}"

        def fetch():
            return self._db.get_penyedia_by_npwp(npwp)

        return self._cache.get_or_set(key, fetch, ttl=TTL_PENYEDIA)

    def create_penyedia(self, data: Dict) -> int:
        """Create penyedia and invalidate cache."""
        result = self._db.create_penyedia(data)
        self._cache.invalidate_pattern("penyedia:*")
        logger.debug("Penyedia cache invalidated")
        return result

    def update_penyedia(self, penyedia_id: int, data: Dict) -> bool:
        """Update penyedia and invalidate cache."""
        result = self._db.update_penyedia(penyedia_id, data)
        self._cache.delete(f"penyedia:{penyedia_id}")
        self._cache.invalidate_pattern("penyedia:all")
        return result

    def delete_penyedia(self, penyedia_id: int) -> bool:
        """Delete penyedia and invalidate cache."""
        result = self._db.delete_penyedia(penyedia_id)
        self._cache.invalidate_pattern("penyedia:*")
        return result

    # =========================================================================
    # PAKET OPERATIONS (cached)
    # =========================================================================

    def get_paket(self, paket_id: int) -> Optional[Dict]:
        """Get paket by ID (cached for 5 minutes)."""
        key = f"paket:{paket_id}"

        def fetch():
            return self._db.get_paket(paket_id)

        return self._cache.get_or_set(key, fetch, ttl=TTL_PAKET_DETAIL)

    def get_paket_list(
        self,
        tahun: int = None,
        status: str = None
    ) -> List[Dict]:
        """Get paket list (cached for 1 minute)."""
        key = self._make_key("paket:list", tahun=tahun, status=status)

        def fetch():
            return self._db.get_paket_list(tahun=tahun, status=status)

        return self._cache.get_or_set(key, fetch, ttl=TTL_PAKET_LIST)

    def create_paket(self, data: Dict) -> int:
        """Create paket and invalidate cache."""
        result = self._db.create_paket(data)
        self._cache.invalidate_pattern("paket:*")
        self._cache.invalidate_pattern("stats:*")
        self._cache.invalidate_pattern("saldo:*")
        logger.debug("Paket cache invalidated")
        return result

    def update_paket(self, paket_id: int, data: Dict) -> bool:
        """Update paket and invalidate cache."""
        result = self._db.update_paket(paket_id, data)
        self._cache.delete(f"paket:{paket_id}")
        self._cache.invalidate_pattern("paket:list:*")
        self._cache.invalidate_pattern("stats:*")
        return result

    def delete_paket(self, paket_id: int) -> bool:
        """Delete paket and invalidate cache."""
        result = self._db.delete_paket(paket_id)
        self._cache.invalidate_pattern("paket:*")
        self._cache.invalidate_pattern("stats:*")
        self._cache.invalidate_pattern("saldo:*")
        return result

    # =========================================================================
    # TEMPLATE OPERATIONS (cached)
    # =========================================================================

    def get_template(self, code: str) -> Optional[Dict]:
        """Get template by code (cached for 1 hour)."""
        key = f"template:{code}"

        def fetch():
            return self._db.get_template(code)

        return self._cache.get_or_set(key, fetch, ttl=TTL_TEMPLATE)

    def get_all_templates(self) -> List[Dict]:
        """Get all templates (cached for 1 hour)."""
        key = "template:all"

        def fetch():
            return self._db.get_all_templates()

        return self._cache.get_or_set(key, fetch, ttl=TTL_TEMPLATE)

    # =========================================================================
    # WORKFLOW OPERATIONS (cached)
    # =========================================================================

    def get_workflow_status(self, paket_id: int) -> List[Dict]:
        """Get workflow status (cached for 1 minute)."""
        key = f"workflow:{paket_id}"

        def fetch():
            return self._db.get_workflow_status(paket_id)

        return self._cache.get_or_set(key, fetch, ttl=TTL_WORKFLOW)

    def update_stage_status(
        self,
        paket_id: int,
        stage_code: str,
        status: str,
        completed_by: str = None,
        notes: str = None
    ) -> bool:
        """Update workflow stage and invalidate cache."""
        result = self._db.update_stage_status(
            paket_id, stage_code, status, completed_by, notes
        )
        self._cache.delete(f"workflow:{paket_id}")
        self._cache.delete(f"paket:{paket_id}")
        return result

    # =========================================================================
    # ITEM BARANG OPERATIONS (cached)
    # =========================================================================

    def get_item_barang(self, paket_id: int) -> List[Dict]:
        """Get item barang for paket (cached for 5 minutes)."""
        key = f"item:paket:{paket_id}"

        def fetch():
            return self._db.get_item_barang(paket_id)

        return self._cache.get_or_set(key, fetch, ttl=TTL_PAKET_DETAIL)

    def get_item_barang_summary(self, paket_id: int) -> Dict:
        """Get item barang summary (cached for 5 minutes)."""
        key = f"item:summary:{paket_id}"

        def fetch():
            return self._db.get_item_barang_summary(paket_id)

        return self._cache.get_or_set(key, fetch, ttl=TTL_PAKET_DETAIL)

    def update_item_barang(self, item_id: int, data: Dict) -> bool:
        """Update item barang and invalidate related cache."""
        result = self._db.update_item_barang(item_id, data)
        # Invalidate item caches (we don't have paket_id here easily)
        self._cache.invalidate_pattern("item:*")
        return result

    def delete_item_barang(self, item_id: int) -> bool:
        """Delete item barang and invalidate cache."""
        result = self._db.delete_item_barang(item_id)
        self._cache.invalidate_pattern("item:*")
        return result

    # =========================================================================
    # STATISTICS (cached)
    # =========================================================================

    def get_statistics(self, mekanisme: str = None) -> Dict:
        """
        Get statistics (cached for 1 minute).

        This is a convenience method - the actual implementation
        depends on how statistics are calculated in the app.
        """
        key = self._make_key("stats", mekanisme=mekanisme)

        def fetch():
            # Calculate statistics from paket list
            paket_list = self._db.get_paket_list()

            total = len(paket_list)
            total_nilai = sum(p.get('nilai_kontrak', 0) or 0 for p in paket_list)

            # Count by status
            by_status = {}
            for p in paket_list:
                status = p.get('status', 'unknown')
                by_status[status] = by_status.get(status, 0) + 1

            return {
                'total': total,
                'total_nilai': total_nilai,
                'by_status': by_status,
            }

        return self._cache.get_or_set(key, fetch, ttl=TTL_STATS)

    def get_saldo_up(self) -> Dict:
        """
        Get UP balance (cached for 30 seconds).

        This is a placeholder - actual implementation depends on
        how UP balance is tracked in the application.
        """
        key = "saldo:up"

        def fetch():
            # This would normally query UP transactions
            # Placeholder implementation
            return {
                'saldo_awal': 0,
                'total_pencairan': 0,
                'total_pengembalian': 0,
                'saldo_akhir': 0,
            }

        return self._cache.get_or_set(key, fetch, ttl=TTL_SALDO)

    # =========================================================================
    # PASS-THROUGH METHODS
    # =========================================================================

    def __getattr__(self, name: str) -> Any:
        """
        Pass through any unknown methods to the underlying database manager.

        This allows CachedDatabaseManager to be used as a drop-in replacement
        for DatabaseManager.
        """
        return getattr(self._db, name)


# =============================================================================
# FACTORY FUNCTION
# =============================================================================


_cached_db_instance: Optional[CachedDatabaseManager] = None


def get_cached_db_manager() -> CachedDatabaseManager:
    """
    Get singleton CachedDatabaseManager instance.

    Returns:
        CachedDatabaseManager instance
    """
    global _cached_db_instance
    if _cached_db_instance is None:
        _cached_db_instance = CachedDatabaseManager()
    return _cached_db_instance


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    'CachedDatabaseManager',
    'get_cached_db_manager',

    # TTL constants
    'TTL_SATKER',
    'TTL_PEGAWAI',
    'TTL_PENYEDIA',
    'TTL_PAKET_DETAIL',
    'TTL_PAKET_LIST',
    'TTL_STATS',
    'TTL_SALDO',
    'TTL_TEMPLATE',
    'TTL_WORKFLOW',
]

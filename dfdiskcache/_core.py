import hashlib
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Union

import pandas as pd
from simplesqlite import SimpleSQLite
from simplesqlite.model import Integer, Model, Text
from simplesqlite.query import And, Set, Where

from .logger import MODULE_NAME, logger  # type: ignore


try:
    from typing import Final  # type: ignore
except ImportError:
    from typing_extensions import Final


def get_utcnow_timestamp() -> int:
    """Get current UTC timestamp in seconds."""

    return int(datetime.now(timezone.utc).timestamp())


def _gen_default_cache_dir_path() -> Path:
    return Path.home() / ".cache" / MODULE_NAME


class DiskCacheInfo(Model):
    key = Text(primary_key=True)
    path = Text(not_null=True)
    created_at = Integer(not_null=True)
    updated_at = Integer(not_null=True)
    ttl = Integer(not_null=True)


class DataFrameDiskCache:
    DEFAULT_TTL = 3600
    PICKLE_EXT = "pkl"

    def __init__(self, cache_dir_path: Union[str, Path, None] = None) -> None:
        if not cache_dir_path:
            self.__cache_dir_path: Final[Path] = _gen_default_cache_dir_path()
        else:
            self.__cache_dir_path = Path(cache_dir_path)

        self.__create_cache_dir()
        self.__con = SimpleSQLite(self.__cache_db_path, mode="a")
        DiskCacheInfo.attach(self.__con)
        DiskCacheInfo.create()

    def __getitem__(self, key: str) -> Optional[pd.DataFrame]:
        return self.get(key)

    def __setitem__(self, key: str, value: pd.DataFrame) -> None:
        self.set(key, value)

    def __delitem__(self, key: str) -> None:
        self.delete(key)

    def __contains__(self, key: str) -> bool:
        return self.get(key) is not None

    def __del__(self) -> None:
        self.prune()
        DiskCacheInfo.commit()

    @property
    def cache_dir_path(self) -> Path:
        return self.__cache_dir_path

    @property
    def __cache_db_path(self) -> Path:
        return self.cache_dir_path / "cache.sqlite3"

    def __create_cache_dir(self) -> None:
        self.cache_dir_path.mkdir(parents=True, exist_ok=True)
        self.__cache_db_path.parent.mkdir(parents=True, exist_ok=True)

    def __calc_hash(self, key: str) -> str:
        return hashlib.sha256(key.strip().encode()).hexdigest()

    def get(self, key: str) -> Optional[pd.DataFrame]:
        hash = self.__calc_hash(key)
        utcnow_timestamp = get_utcnow_timestamp()
        results = DiskCacheInfo.select(
            where=And(
                [
                    Where(DiskCacheInfo.key, hash),
                    f"(updated_at + ttl) >= {utcnow_timestamp}",
                ]
            )
        )
        for record in results:
            if not os.path.isfile(record.path):
                # delete the invalid cache entry
                return None

            logger.debug(f"cache found: {record}")

            return pd.read_pickle(record.path)

        logger.debug(f"valid cache not found: hash={hash}")

        return None

    def set(self, key: str, value: pd.DataFrame, ttl: Optional[int] = None) -> str:
        hash = self.__calc_hash(key)
        tmp_fpath = os.path.join(
            tempfile.gettempdir(),
            f"{MODULE_NAME}_{hash}_{get_utcnow_timestamp():d}.{self.PICKLE_EXT}",
        )
        cache_fpath = self.cache_dir_path / f"{hash}.{self.PICKLE_EXT}"

        value.to_pickle(tmp_fpath)
        os.rename(tmp_fpath, cache_fpath)

        utcnow_timestamp = get_utcnow_timestamp()
        num_record = DiskCacheInfo.fetch_num_records(where=Where(DiskCacheInfo.key, hash))

        if num_record == 0:
            if ttl is None:
                ttl = self.DEFAULT_TTL
            assert ttl is not None

            DiskCacheInfo.insert(
                DiskCacheInfo(
                    key=hash,
                    path=str(cache_fpath),
                    ttl=ttl,
                    created_at=utcnow_timestamp,
                    updated_at=utcnow_timestamp,
                )
            )
        else:
            DiskCacheInfo.update(
                set_query=[
                    Set(DiskCacheInfo.path, str(cache_fpath)),
                    Set(DiskCacheInfo.updated_at, utcnow_timestamp),
                ],
                where=Where(DiskCacheInfo.key, hash),
            )

        return hash

    def touch(self, key: str) -> Optional[str]:
        hash = self.__calc_hash(key)
        utcnow_timestamp = get_utcnow_timestamp()

        for record in DiskCacheInfo.select(where=Where(DiskCacheInfo.key, hash)):
            logger.debug(f"touching: {record}")
            DiskCacheInfo.update(
                set_query=[Set(DiskCacheInfo.updated_at, utcnow_timestamp)],
                where=Where(DiskCacheInfo.key, record.key),
            )
            return hash

        return None

    def prune(self) -> int:
        where = f"(updated_at + ttl) < {get_utcnow_timestamp()}"
        delete_ct = 0

        logger.debug(f"pruning {self.__cache_db_path}")

        for record in DiskCacheInfo.select(where=where):
            logger.debug(f"deleting: {record}")
            if os.path.isfile(record.path):
                os.remove(record.path)

            delete_ct += 1

        DiskCacheInfo.delete(where=where)
        logger.debug(f"pruned {delete_ct} expired cache entries")

        return delete_ct

    def delete(self, key: str) -> str:
        hash = self.__calc_hash(key)
        where = Where(DiskCacheInfo.key, hash)

        for record in DiskCacheInfo.select(where=where):
            logger.debug(f"deleting: {record}")
            if os.path.isfile(record.path):
                os.remove(record.path)

        DiskCacheInfo.delete(where=where)

        return hash

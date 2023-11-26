import time
from pathlib import Path

import pandas as pd
import pytest

from dfdiskcache import DataFrameDiskCache


class Test_DataFrameDiskCache_cache_dir_path:
    @pytest.mark.parametrize(
        ["value", "expected"],
        [
            [None, Path.home() / ".cache" / "dfdiskcache"],
            ["/tmp/cache", Path("/tmp/cache")],
        ],
    )
    def test_normal(self, value, expected):
        cache = DataFrameDiskCache(value)
        assert cache.cache_dir_path == expected


class Test_DataFrameDiskCache_methods:
    def test_normal(self, tmp_path):
        cache = DataFrameDiskCache(tmp_path)
        key = "test"
        not_exist_key = "not_exist"
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})

        assert key not in cache
        assert cache.get(key) is None

        # test set/get and __contains__ methods
        hash = cache.set(key, df, ttl=1)
        assert hash
        assert key in cache
        assert cache.get(key).equals(df)
        assert not_exist_key not in cache

        # confirm cache expiration
        time.sleep(2)  # wait for cache expiration
        assert cache.get(key) is None

        # test touch method
        assert cache.touch(key)
        assert cache.get(key) is not None  # touch method updates cache updated_at
        time.sleep(2)  # wait for cache expiration

        # prune must delete expired cache
        assert cache.prune() == 1

        # test delete method
        hash = cache.set(key, df)
        assert hash == cache.delete(key)


class Test_DataFrameDiskCache_operations:
    def test_normal(self, tmp_path):
        cache = DataFrameDiskCache(tmp_path)
        key = "test"
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})

        assert key not in cache
        assert cache[key] is None
        cache[key] = df
        assert key in cache
        assert cache[key].equals(df)
        assert cache.get(key).equals(df)
        del cache[key]
        assert cache[key] is None
        assert cache.get(key) is None

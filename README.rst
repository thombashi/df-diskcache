.. contents:: **df-diskcache**
   :backlinks: top
   :depth: 2


Summary
============================================

``df-diskcache`` is a Python library for caching ``pandas.DataFrame`` objects to local disk.

.. image:: https://github.com/thombashi/df-diskcache/actions/workflows/ci.yml/badge.svg
    :target: https://github.com/thombashi/df-diskcache/actions/workflows/ci.yml
    :alt: CI status of Linux/macOS/Windows

.. image:: https://coveralls.io/repos/github/thombashi/df-diskcache/badge.svg?branch=master
    :target: https://coveralls.io/github/thombashi/df-diskcache?branch=master
    :alt: Test coverage: coveralls

.. image:: https://github.com/thombashi/df-diskcache/actions/workflows/github-code-scanning/codeql/badge.svg
    :target: https://github.com/thombashi/df-diskcache/actions/workflows/github-code-scanning/codeql
    :alt: CodeQL


Installation
============================================
::

    pip install df-diskcache


Features
============================================

Supports the following methods:

- ``get``: Get a cache entry (``pandas.DataFrame``) for the key. Returns ``None`` if the key is not found.
- ``set``: Create a cache entry with an optional time-to-live (TTL) for the key-value pair.
- ``update``
- ``touch``: Update the last accessed time of a cache entry to extend the TTL.
- ``delete``
- ``prune``: Delete expired cache entries.
- Dictionary-like operations:
    - ``__getitem__``
    - ``__setitem__``
    - ``__contains__``
    - ``__delitem__``


Usage
============================================

:Sample Code:
    .. code-block:: python

        import pandas as pd
        from dfdiskcache import DataFrameDiskCache

        cache = DataFrameDiskCache()
        url = "https://raw.githubusercontent.com/pandas-dev/pandas/v2.1.3/pandas/tests/io/data/csv/iris.csv"

        df = cache.get(url)
        if df is None:
            print("cache miss")
            df = pd.read_csv(url)
            cache.set(url, df)
        else:
            print("cache hit")

        print(df)

You can also use operations like a dictionary:

:Sample Code:
    .. code-block:: python

        import pandas as pd
        from dfdiskcache import DataFrameDiskCache

        cache = DataFrameDiskCache()
        url = "https://raw.githubusercontent.com/pandas-dev/pandas/v2.1.3/pandas/tests/io/data/csv/iris.csv"

        df = cache[url]
        if df is None:
            print("cache miss")
            df = pd.read_csv(url)
            cache[url] = df
        else:
            print("cache hit")

        print(df)


Dependencies
============================================
- Python 3.7+
- `Python package dependencies (automatically installed) <https://github.com/thombashi/df-diskcache/network/dependencies>`__

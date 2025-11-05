.. contents:: **df-diskcache**
   :backlinks: top
   :depth: 2


Summary
============================================

``df-diskcache`` is a Python library for caching ``pandas.DataFrame`` objects to local disk.

.. image:: https://badge.fury.io/py/df-diskcache.svg
    :target: https://badge.fury.io/py/df-diskcache
    :alt: PyPI package version

.. image:: https://img.shields.io/pypi/pyversions/df-diskcache.svg
    :target: https://pypi.org/project/df-diskcache
    :alt: Supported Python versions

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

Basic Usage
--------------------------------------------

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


Cache existence check
--------------------------------------------
You can check if a cache entry exists by using the ``in`` operator.

.. code-block:: python

    import pandas as pd
    from dfdiskcache import DataFrameDiskCache

    cache = DataFrameDiskCache()
    url = "https://raw.githubusercontent.com/pandas-dev/pandas/v2.1.3/pandas/tests/io/data/csv/iris.csv"

    if url in cache:
        print("cache exists")
        df = cache[url]
    else:
        print("cache does not exist")


Set TTL for cache entries
--------------------------------------------
You can set the default TTL for cache entries by setting the ``DataFrameDiskCache.DEFAULT_TTL`` or the ``ttl`` parameter of the ``set`` method.

.. code-block:: python

    import pandas as pd
    from dfdiskcache import DataFrameDiskCache

    DataFrameDiskCache.DEFAULT_TTL = 10  # you can override the default TTL (default: 3600 seconds)

    cache = DataFrameDiskCache()
    url = "https://raw.githubusercontent.com/pandas-dev/pandas/v2.1.3/pandas/tests/io/data/csv/iris.csv"

    df = cache.get(url)
    if df is None:
        df = pd.read_csv(url)
        cache.set(url, df, ttl=60)  # you can set a TTL for the key-value pair

    print(df)


Delete cache entries
--------------------------------------------
You can delete a cache entry by using the ``del`` operator or the ``delete`` method.

.. code-block:: python

    import pandas as pd
    from dfdiskcache import DataFrameDiskCache

    cache = DataFrameDiskCache()

    key = "example key"
    if key not in cache:
        df = pd.DataFrame([["a", 1], ["b", 2]], columns=["col_a", "col_b"])
        cache.set(key, df)

    # delete a cache entry by using del operator
    del cache[url]
    
    # delete a cache entry by using delete method
    cache.delete(url)


Cache lifetime management
--------------------------------------------
Expired cache entries are automatically deleted when you access a cache entry or invoke the ``prune`` method.

You can refresh the last accessed time of a cache entry by using the ``touch`` method.


Dependencies
============================================
- Python 3.9+
- `Python package dependencies (automatically installed) <https://github.com/thombashi/df-diskcache/network/dependencies>`__

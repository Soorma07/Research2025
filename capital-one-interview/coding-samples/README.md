# Capital One Coding Samples

This directory contains Python coding samples commonly asked in Capital One backend engineering interviews.

## Coding Samples

1. **01_transaction_analysis.py** - Suspicious account detection using sliding windows
2. **02_rate_limiter.py** - Rate limiter implementations (sliding window, token bucket, leaky bucket, fixed window)
3. **03_account_merging.py** - Account merging using Union-Find data structure
4. **04_lru_cache.py** - LRU and LFU cache implementations
5. **05_credit_card_validation.py** - Credit card validation (Luhn algorithm, card type detection, masking)
6. **06_graph_problems.py** - Graph algorithms (BFS, DFS, Dijkstra, cycle detection, fraud ring detection)

## Running the Tests

### Prerequisites

Install pytest:

```bash
pip install pytest
```

### Run All Tests

From the `coding-samples` directory:

```bash
pytest tests/ -v
```

### Run Tests for a Specific Module

```bash
pytest tests/test_transaction_analysis.py -v
pytest tests/test_rate_limiter.py -v
pytest tests/test_account_merging.py -v
pytest tests/test_lru_cache.py -v
pytest tests/test_credit_card_validation.py -v
pytest tests/test_graph_problems.py -v
```

### Run a Specific Test Class

```bash
pytest tests/test_lru_cache.py::TestLRUCache -v
pytest tests/test_rate_limiter.py::TestTokenBucketRateLimiter -v
```

### Run a Specific Test Method

```bash
pytest tests/test_credit_card_validation.py::TestLuhnChecksum::test_valid_visa -v
```

### Expected Output

```
============================= test session starts ==============================
platform linux -- Python 3.x.x, pytest-x.x.x
collected 117 items

tests/test_account_merging.py::TestUnionFind::test_find_creates_new_set PASSED
tests/test_account_merging.py::TestUnionFind::test_union_connects_elements PASSED
...
======================= 117 passed in X.XXs ========================
```

## Running Individual Samples

Each coding sample can also be run directly to execute its built-in tests:

```bash
python 01_transaction_analysis.py
python 02_rate_limiter.py
python 03_account_merging.py
python 04_lru_cache.py
python 05_credit_card_validation.py
python 06_graph_problems.py
```

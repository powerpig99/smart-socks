# Smart Socks Testing Guide

**ELEC-E7840 Smart Wearables — Aalto University**

---

## Overview

This guide covers testing strategies for the Smart Socks project, including unit tests, integration tests, and hardware validation.

---

## Test Structure

```
tests/
├── __init__.py
├── conftest.py                  # Pytest configuration and fixtures
├── TESTING_GUIDE.md            # This file
├── test_data_validation.py     # Data quality validation tests
├── test_feature_extraction.py  # Feature extraction tests (TODO)
├── test_train_model.py         # Model training tests (TODO)
├── test_preprocessing.py       # Data preprocessing tests (TODO)
└── fixtures/                   # Test data files
    ├── sample_sensor_data.csv
    └── expected_features.csv
```

---

## Running Tests

### Run All Tests

```bash
cd 04_Code/python/
pytest tests/ -v
```

### Run Specific Test File

```bash
pytest tests/test_data_validation.py -v
```

### Run with Coverage Report

```bash
pip install pytest-cov
pytest tests/ --cov=. --cov-report=html
```

### Run Tests Matching Pattern

```bash
pytest tests/ -v -k "validation"  # Run tests with "validation" in name
```

---

## Test Categories

### 1. Unit Tests

Test individual functions in isolation.

**Examples:**
- Data validation functions
- Feature extraction algorithms
- Utility functions

```python
def test_stuck_sensor_detection():
    df = create_stuck_sensor_data()
    stuck = check_stuck_sensors(df)
    assert len(stuck) > 0
```

### 2. Integration Tests

Test interaction between components.

**Examples:**
- Full pipeline from raw data to features
- Model training and prediction
- Serial communication flow

```python
def test_full_pipeline():
    raw_data = load_test_data()
    processed = preprocess(raw_data)
    features = extract_features(processed)
    model = train_model(features)
    assert model.accuracy > 0.8
```

### 3. Hardware Tests

Test with actual hardware (run manually).

**Examples:**
- Sensor connectivity
- ADC reading accuracy
- BLE connection stability

```bash
python quick_test.py --port /dev/ttyUSB0
```

---

## Fixtures

Fixtures provide test data and are defined in `conftest.py`.

### Available Fixtures

| Fixture | Description |
|---------|-------------|
| `sample_sensor_data` | Valid synthetic sensor data |
| `invalid_sensor_data` | Data with sensor issues |
| `missing_timestamp_data` | Data with timestamp problems |
| `temp_output_dir` | Temporary directory for outputs |
| `test_data_dir` | Path to test fixtures |

### Using Fixtures

```python
def test_my_function(sample_sensor_data):
    result = my_function(sample_sensor_data)
    assert result is not None
```

---

## Writing New Tests

### Test Template

```python
#!/usr/bin/env python3
"""Tests for my_module."""

import pytest
from my_module import my_function


class TestMyFeature:
    """Test suite for my feature."""
    
    def test_basic_functionality(self):
        """Test basic functionality."""
        input_data = [1, 2, 3]
        result = my_function(input_data)
        assert result == expected_output
    
    def test_edge_case(self):
        """Test edge case handling."""
        with pytest.raises(ValueError):
            my_function(invalid_input)
    
    def test_with_fixture(self, sample_sensor_data):
        """Test using fixture."""
        result = my_function(sample_sensor_data)
        assert len(result) > 0
```

### Best Practices

1. **Descriptive Names**: Test names should describe what's being tested
2. **One Assertion**: Ideally one logical assertion per test
3. **Use Fixtures**: Don't duplicate test data creation
4. **Docstrings**: Explain what the test is checking
5. **Edge Cases**: Test boundary conditions and error cases

---

## Test Data

### Creating Synthetic Data

```python
def create_test_data(n_samples=100, sample_rate=50):
    """Create synthetic sensor data."""
    data = {
        'time_ms': np.arange(n_samples) * (1000 / sample_rate),
    }
    
    for sensor in SENSORS['names']:
        data[sensor] = np.random.randint(500, 1500, n_samples)
    
    return pd.DataFrame(data)
```

### Recording Real Test Data

```python
# From actual hardware session
df = pd.read_csv('real_session.csv')
df.to_csv('tests/fixtures/real_data.csv', index=False)
```

---

## Continuous Testing

### Pre-Commit Checks

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: pytest
        name: Run tests
        entry: pytest tests/ -v --tb=short
        language: system
        pass_filenames: false
        always_run: true
```

### CI/CD Integration

GitHub Actions example:

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest tests/ -v
```

---

## Hardware Testing

### Manual Test Checklist

Before each major milestone:

- [ ] All 10 sensors respond to pressure
- [ ] No stuck or saturated sensors
- [ ] Timestamps are consistent
- [ ] Dropout rate < 20%
- [ ] BLE connection stable for 5+ minutes
- [ ] Real-time classification responsive

### Automated Hardware Test

```bash
python quick_test.py --port /dev/ttyUSB0 --duration 30
```

---

## Debugging Failed Tests

### Verbose Output

```bash
pytest tests/test_data_validation.py -v --tb=long
```

### Print Debugging

```python
def test_with_debug(sample_sensor_data):
    print(f"Data shape: {sample_sensor_data.shape}")
    print(f"First few rows:\n{sample_sensor_data.head()}")
    # ... test code
```

### PDB Debugging

```python
import pytest

def test_with_pdb(sample_sensor_data):
    result = process_data(sample_sensor_data)
    pytest.set_trace()  # Drop into debugger
    assert result is not None
```

---

## Coverage Goals

| Module | Target Coverage |
|--------|----------------|
| data_validation.py | 90% |
| feature_extraction.py | 80% |
| train_model.py | 70% |
| data_preprocessing.py | 80% |
| real_time_classifier.py | 60% |

---

## Common Issues

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'config'`

**Solution:** Run tests from `04_Code/python/` directory:
```bash
cd 04_Code/python/
pytest tests/
```

### Fixture Not Found

**Problem:** Fixture not available

**Solution:** Ensure `conftest.py` is in tests directory and contains fixture.

### Tests Pass Individually but Fail Together

**Problem:** Shared state between tests

**Solution:** Use fixtures with `scope="function"` (default) and avoid global variables.

---

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Python Testing Best Practices](https://realpython.com/python-testing/)
- [Test-Driven Development](https://testdriven.io/)

---

*Last updated: 2026-01-29*

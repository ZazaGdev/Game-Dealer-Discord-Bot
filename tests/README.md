# GameDealer Test Suite

This directory contains all test files for the GameDealer bot project.

## Test Structure

### Primary Test Files

-   **test_comprehensive.py** - **Main test suite** - Consolidated tests for all functionality
-   **test_priority_sorting.py** - **Priority-based sorting verification** - Tests new sorting logic
-   **test_priority_search.py** - **Priority search verification** - Tests strict priority filtering
-   **test_database.py** - **Database loading test** - Verifies priority games database

### Utility Test Files

-   **test_bot_deals.py** - Deal fetching and Discord bot integration tests
-   **debug_api.py** - API debugging and troubleshooting script

## Recommended Usage

### Quick Full Test (Recommended)

Run the comprehensive test suite for complete validation:

```bash
python tests/test_comprehensive.py
```

### Legacy Individual Tests

Run specific test files for targeted testing:

```bash
# From the project root directory
python tests/test_api.py
python tests/test_bot_fixes.py
python tests/test_new_features.py
python tests/test_search.py
```

### Debug Mode

For troubleshooting API issues:

```bash
python tests/debug_api.py
```

### Bot Integration Test

For testing Discord bot integration:

```bash
python tests/test_bot_deals.py
```

### Priority Sorting Test

For testing the new priority-based sorting logic:

```bash
python tests/test_priority_sorting.py
```

### Priority Search Test

For testing strict priority filtering functionality:

```bash
python tests/test_priority_search.py
```

### Database Test

For testing priority games database loading:

```bash
python tests/test_database.py
```

### Pytest (Alternative)

Or use pytest if you prefer:

```bash
pip install pytest
pytest tests/
```

## Test Coverage

The comprehensive test suite covers:

-   ✅ API connectivity and authentication
-   ✅ Priority game filtering system
-   ✅ **NEW**: Priority-based sorting (priority > discount when discount > 50%)
-   ✅ Store-specific filtering
-   ✅ Deal quality parameters
-   ✅ Error handling scenarios
-   ✅ Database loading and validation
-   ✅ Exact item count compliance

## Requirements

Make sure you have a valid ITAD_API_KEY in your .env file before running the tests.

## Migration Notes

The `test_comprehensive.py` file consolidates functionality from multiple legacy test files. Consider migrating remaining tests to the comprehensive suite for better maintainability.

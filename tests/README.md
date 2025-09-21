# Tests Directory

This directory contains test scripts for the GameDealer bot.

## Test Files

-   **test_api.py** - Basic ITAD API connectivity and deal fetching tests
-   **test_bot_fixes.py** - Tests for the fixed bot functionality (error handling, store filtering)
-   **test_new_features.py** - Tests for new features like store filtering and API response logging
-   **test_search.py** - Basic ITAD API search functionality tests

## Running Tests

To run the tests, use:

```bash
# From the project root directory
python tests/test_api.py
python tests/test_bot_fixes.py
# etc.
```

Or use pytest if you prefer:

```bash
pip install pytest
pytest tests/
```

## Note

Make sure you have a valid ITAD_API_KEY in your .env file before running the tests.

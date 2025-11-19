# Testing Directory

This directory contains test scripts and test documentation for the BM Parliament portal.

## Structure

- **Test Scripts** - Python test files for integration and E2E testing
- **Test Documentation** - Test plans and reports

## Test Files

### Sector-Specific Tests
- **`test_cancer_dialysis_sector.py`** - Tests for cancer/dialysis patient sector registration
- **`test_madaris_sector.py`** - Tests for Madaris teacher sector registration
- **`simple_test_cancer_dialysis.py`** - Simplified cancer/dialysis sector tests
- **`simple_test_madaris.py`** - Simplified Madaris sector tests

### Registration Flow Tests
- **`test_registration_flow.py`** - End-to-end member registration tests

### System Status Tests
- **`check_program_status.py`** - Verify program status and visibility
- **`check_status.py`** - General system health checks

### Other Tests
- **`test_pandas_django.py`** - Pandas integration with Django ORM tests

## Running Tests

### Individual Test Files
```bash
# From project root
cd testing
python3 test_registration_flow.py
```

### Django Test Suite
```bash
# Run all Django tests
python3 src/manage.py test

# Run specific app tests
python3 src/manage.py test apps.constituents
```

### Docker Environment
```bash
# Run tests in Docker
docker-compose exec web python manage.py test
```

## Test Documentation

- **`test_plan.md`** - Comprehensive test plan
- **`run_tests.sh`** - Automated test runner script

## Writing Tests

Follow Django testing best practices:
1. Use Django's `TestCase` for database tests
2. Use `SimpleTestCase` for non-database tests
3. Name test methods with `test_` prefix
4. Group related tests in test classes
5. Use meaningful assertion messages

Example:
```python
from django.test import TestCase
from apps.constituents.models import FahanieCaresmember

class MemberRegistrationTests(TestCase):
    def test_member_creation(self):
        """Test that a member can be created successfully"""
        member = FahanieCaresmember.objects.create(
            first_name="Juan",
            last_name="Dela Cruz",
            sector="Senior Citizens"
        )
        self.assertEqual(member.first_name, "Juan")
```

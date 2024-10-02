
import json
import logging
import requests
import pytest
from utils.env import (
    TEST_USER_USERNAME, TEST_USER_PASSWORD
)
from tests.utils.config import get_base_url


# Set up the logger
logging.basicConfig(
    level=logging.DEBUG,
    format='pytest:%(levelname)s:\t%(message)s',
)
logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def base_url():
    """Fixture for base URL used in all tests."""
    return get_base_url()


@pytest.fixture(scope="session")
def access_token(base_url):
    """Obtain the access token to be used in all test cases."""
    url = f"{base_url}/auth/token"
    data = {
        "username": TEST_USER_USERNAME,
        "password": TEST_USER_PASSWORD
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(url, headers=headers, data=data)
    
    # Check if the token exists and return it
    token = response.json().get("access_token")
    if not token:
        pytest.fail("Failed to obtain access token", pytrace=False)
    
    return token


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Hook to print the JSON report to stdout at the end of the test session."""
    results = []

    # Collect test results
    for test in terminalreporter.stats.get('passed', []):
        results.append({
            "nodeid": test.nodeid,
            "outcome": "passed",
            "duration": getattr(test, "duration", 0),
        })

    for test in terminalreporter.stats.get('failed', []):
        results.append({
            "nodeid": test.nodeid,
            "outcome": "failed",
            "duration": getattr(test, "duration", 0),
        })

    summary = {
        "total": terminalreporter._numcollected,
        "passed": len(terminalreporter.stats.get('passed', [])),
        "failed": len(terminalreporter.stats.get('failed', []))
    }

    report = {
        "pytest_report": {
            "tests": results,
            "summary": summary
        }
    }

    # Write the JSON report to stdout as a single line
    logger.info(json.dumps(report, separators=(',', ':')))

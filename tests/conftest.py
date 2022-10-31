import pytest
import os

@pytest.fixture(autouse=True, scope="session")
def clear_db():
    try:
        os.unlink("test.db")
    finally:
        yield True
    try:
        os.unlink("test.db")
    finally:
        pass

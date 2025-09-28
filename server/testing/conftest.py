# #!/usr/bin/env python3

# def pytest_itemcollected(item):
#     par = item.parent.obj
#     node = item.obj
#     pref = par.__doc__.strip() if par.__doc__ else par.__class__.__name__
#     suf = node.__doc__.strip() if node.__doc__ else node.__name__
#     if pref or suf:
#         item._nodeid = ' '.join((pref, suf))


import pytest
from config import app, db
from models import User, Recipe
from app import app,db


@pytest.fixture(autouse=True)
def run_around_tests():
    """
    Auto-use fixture: before each test, create tables in an in-memory DB.
    After each test, drop everything so tests are isolated.
    """
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_ECHO"] = False

    with app.app_context():
        db.drop_all()
        db.create_all()
    yield
    with app.app_context():
        db.session.remove()
        db.drop_all()
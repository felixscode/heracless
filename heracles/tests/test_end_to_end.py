"""
testing the app
"""
from heracles.decorator import heracles
from heracles.tests.load import filled_config


@heracles()
def test_decorator(cfg):
    assert cfg == filled_config()

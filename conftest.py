import pytest
from django.contrib.auth import get_user_model
from trades.tests.factories import UserFactory, StockFactory

User = get_user_model()

@pytest.fixture
def test_user():
    return UserFactory()

@pytest.fixture
def test_stock():
    return StockFactory()

@pytest.fixture
def test_trade(test_user, test_stock):
    from trades.tests.factories import TradeFactory
    return TradeFactory(user=test_user, stock=test_stock)
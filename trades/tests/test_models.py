import pytest
from trades.models import Stock, Trade
from trades.tests.factories import StockFactory, TradeFactory

@pytest.mark.django_db
def test_stock_creation():
    stock = StockFactory()
    assert Stock.objects.count() == 1
    assert str(stock) == f"{stock.id} - {stock.name}"

@pytest.mark.django_db
def test_trade_creation():
    trade = TradeFactory()
    assert Trade.objects.count() == 1
    assert trade.value == trade.quantity * trade.price_at_trade
    assert trade.trade_type in ['BUY', 'SELL']
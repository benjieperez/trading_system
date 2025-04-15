import pytest
from trades.serializers import TradeSerializer
from trades.tests.factories import StockFactory, UserFactory

@pytest.mark.django_db
def test_trade_serializer():
    user = UserFactory()
    stock = StockFactory()
    
    data = {
        'stock_id': stock.id,
        'trade_type': 'BUY',
        'quantity': 10
    }
    
    serializer = TradeSerializer(data=data, context={'request': type('obj', (), {'user': user})})
    assert serializer.is_valid()
    trade = serializer.save()
    assert trade.user == user
    assert trade.price_at_trade == stock.price

@pytest.mark.django_db
def test_invalid_trade_serializer():
    serializer = TradeSerializer(data={'trade_type': 'BUY', 'quantity': 0})
    assert not serializer.is_valid()
    assert 'stock_id' in serializer.errors
    assert 'quantity' in serializer.errors
import pytest
import csv
import os
from io import StringIO
from django.core.management import call_command
from trades.tests.factories import UserFactory, StockFactory
from trades.models import Trade

@pytest.mark.django_db
def test_process_trades_command(tmp_path, settings):
    settings.TRADES_DIR = str(tmp_path)
    user = UserFactory()
    stock = StockFactory()
    
    # Create test CSV
    csv_path = tmp_path / 'trades.csv'
    with open(csv_path, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['user_id', 'stock_id', 'trade_type', 'quantity'])
        writer.writerow([user.id, stock.id, 'BUY', '10'])
    
    # Run command
    call_command('process_trades')
    
    # Verify trade was created
    assert Trade.objects.count() == 1
    trade = Trade.objects.first()
    assert trade.user == user
    assert trade.stock == stock
    assert trade.quantity == 10
    
    # Verify file was moved to processed
    assert not os.path.exists(csv_path)
    assert len(list((tmp_path / 'processed').iterdir())) == 1
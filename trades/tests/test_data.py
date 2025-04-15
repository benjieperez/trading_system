from django.contrib.auth import get_user_model
from trades.models import Stock

def create_test_data():
    User = get_user_model()
    
    # Create test user
    user = User.objects.create_user(
        username='testuser',
        password='testpass123',
        email='test@example.com'
    )
    
    # Mock stocks data
    stocks = [
        {'id': 'AAPL', 'name': 'Apple Inc.', 'price': 175.50},
        {'id': 'GOOGL', 'name': 'Alphabet Inc.', 'price': 135.25},
        {'id': 'MSFT', 'name': 'Microsoft Corporation', 'price': 310.20},
    ]
    
    for stock_data in stocks:
        Stock.objects.create(**stock_data)
    
    return user
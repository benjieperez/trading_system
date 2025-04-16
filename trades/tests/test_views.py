import pytest
from django.urls import reverse
from rest_framework import status
from trades.tests.factories import UserFactory, StockFactory, TradeFactory

@pytest.mark.django_db
class TestTradeAPI:
    @pytest.fixture
    def api_client(self):
        from rest_framework.test import APIClient
        return APIClient()

    @pytest.fixture
    def authenticated_client(self, api_client):
        user = UserFactory()
        api_client.force_authenticate(user=user)
        return api_client, user

    def test_list_trades(self, authenticated_client):
        client, user = authenticated_client
        TradeFactory.create_batch(3, user=user)
        url = reverse('trade-list')
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 3

    def test_create_trade(self, authenticated_client):
        client, user = authenticated_client
        stock = StockFactory()
        url = reverse('trade-list')
        data = {
            'stock_id': stock.id,
            'trade_type': 'BUY',
            'quantity': 10
        }
        response = client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['quantity'] == 10
        assert response.data['stock']['id'] == stock.id

    def test_bulk_trades(self, authenticated_client):
        client, user = authenticated_client
        stock1 = StockFactory()
        stock2 = StockFactory()
        url = reverse('trade-bulk')
        
        # Create properly formatted CSV data
        csv_data = (
            "stock_id,trade_type,quantity\n"
            f"{stock1.id},BUY,10\n"
            f"{stock2.id},SELL,5"
        )
        
        # Create a proper file upload
        from io import StringIO
        file = StringIO(csv_data)
        file.name = 'trades.csv'
        
        response = client.post(
            url,
            {'file': file},
            format='multipart'
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['created'] == 2

    def test_portfolio_view(self, authenticated_client):
        client, user = authenticated_client
        stock = StockFactory(price=100.00)
        TradeFactory(user=user, stock=stock, trade_type='BUY', quantity=10)
        TradeFactory(user=user, stock=stock, trade_type='SELL', quantity=5)
        
        url = reverse('trade-portfolio')
        response = client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['portfolio'][stock.id]['total_quantity'] == 5
        assert float(response.data['portfolio'][stock.id]['total_value']) == 500.00
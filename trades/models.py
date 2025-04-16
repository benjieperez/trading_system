from django.db import models
from django.contrib.auth.models import User

class Stock(models.Model):
    id = models.CharField(primary_key=True, max_length=10)  # Ticker symbol like 'AAPL'
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.id} - {self.name}"

class Trade(models.Model):
    BUY = 'BUY'
    SELL = 'SELL'
    TRADE_TYPES = [
        (BUY, 'Buy'),
        (SELL, 'Sell'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.PROTECT, null=False)
    trade_type = models.CharField(max_length=4, choices=TRADE_TYPES)
    quantity = models.PositiveIntegerField()
    price_at_trade = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    @property
    def value(self):
        return self.quantity * self.price_at_trade
        
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'stock']),
        ]
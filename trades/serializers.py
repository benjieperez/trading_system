from rest_framework import serializers
from .models import Stock, Trade

class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ['id', 'name', 'price']

class TradeSerializer(serializers.ModelSerializer):
    stock = StockSerializer(read_only=True)
    stock_id = serializers.CharField(write_only=True)
    
    class Meta:
        model = Trade
        fields = ['id', 'user', 'stock', 'stock_id', 'trade_type', 'quantity', 
                 'price_at_trade', 'timestamp', 'value']
        read_only_fields = ['user', 'price_at_trade', 'timestamp', 'value']
        
    def validate_stock_id(self, value):
        if not Stock.objects.filter(id=value).exists():
            raise serializers.ValidationError("Stock does not exist")
        return value
        
    def create(self, validated_data):
        stock_id = validated_data.pop('stock_id')
        stock = Stock.objects.get(id=stock_id)
        validated_data['price_at_trade'] = stock.price
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class BulkTradeSerializer(serializers.Serializer):
    file = serializers.FileField()
    
    def validate_file(self, value):
        if not value.name.endswith('.csv'):
            raise serializers.ValidationError("Only CSV files are allowed")
        return value
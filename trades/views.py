from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from .models import Stock, Trade
from .serializers import StockSerializer, TradeSerializer, BulkTradeSerializer
import csv
import os
from django.conf import settings
from datetime import datetime

class TradeViewSet(viewsets.ModelViewSet):
    serializer_class = TradeSerializer
    
    def get_queryset(self):
        return Trade.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'], serializer_class=BulkTradeSerializer)
    def bulk(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        csv_file = serializer.validated_data['file']
        decoded_file = csv_file.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file)
        
        trades = []
        for row in reader:
            try:
                stock = Stock.objects.get(id=row['stock_id'])
                trade = Trade(
                    user=request.user,
                    stock=stock,
                    trade_type=row['trade_type'],
                    quantity=row['quantity'],
                    price_at_trade=stock.price
                )
                trades.append(trade)
            except (Stock.DoesNotExist, KeyError) as e:
                continue
        
        Trade.objects.bulk_create(trades)
        return Response({"status": "success", "created": len(trades)}, 
                       status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def stock_value(self, request):
        stock_id = request.query_params.get('stock_id')
        if not stock_id:
            return Response({"error": "stock_id parameter is required"}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        try:
            stock = Stock.objects.get(id=stock_id)
        except Stock.DoesNotExist:
            return Response({"error": "Stock not found"}, 
                          status=status.HTTP_404_NOT_FOUND)
        
        trades = Trade.objects.filter(user=request.user, stock=stock)
        total_value = sum(trade.value for trade in trades)
        
        return Response({
            "stock": stock_id,
            "total_value": total_value,
            "currency": "USD"
        })

class StockViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from .models import Stock, Trade
from .serializers import StockSerializer, TradeSerializer, BulkTradeSerializer
import csv
import os
from django.conf import settings

class TradeViewSet(viewsets.ModelViewSet):
    serializer_class = TradeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Trade.objects.filter(user=self.request.user).select_related('stock')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
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
                    trade_type=row['trade_type'].upper(),
                    quantity=int(row['quantity']),
                    price_at_trade=stock.price
                )
                trades.append(trade)
            except (Stock.DoesNotExist, KeyError, ValueError) as e:
                continue
        
        with transaction.atomic():
            Trade.objects.bulk_create(trades)
        
        return Response({
            "status": "success",
            "created": len(trades),
            "failed": reader.line_num - 1 - len(trades)
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def portfolio(self, request):
        stocks = {}
        trades = Trade.objects.filter(user=request.user).select_related('stock')
        
        for trade in trades:
            if trade.stock.id not in stocks:
                stocks[trade.stock.id] = {
                    'name': trade.stock.name,
                    'current_price': float(trade.stock.price),
                    'total_quantity': 0,
                    'total_value': 0.0
                }
            
            if trade.trade_type == Trade.BUY:
                stocks[trade.stock.id]['total_quantity'] += trade.quantity
            else:
                stocks[trade.stock.id]['total_quantity'] -= trade.quantity
            
            stocks[trade.stock.id]['total_value'] = (
                stocks[trade.stock.id]['total_quantity'] * 
                stocks[trade.stock.id]['current_price']
            )
        
        return Response({
            'portfolio': stocks,
            'total_value': sum(stock['total_value'] for stock in stocks.values())
        })

class StockViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Stock.objects.all().order_by('id')
    serializer_class = StockSerializer
    permission_classes = [IsAuthenticated]
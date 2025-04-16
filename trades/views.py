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
        
        # Validate required columns
        required_columns = ['stock_id', 'trade_type', 'quantity']
        if not all(col in reader.fieldnames for col in required_columns):
            return Response(
                {"error": f"CSV must contain these columns: {', '.join(required_columns)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        trades = []
        success_count = 0
        errors = []
        
        for row_num, row in enumerate(reader, start=2):  # row_num starts at 2 (header is row 1)
            try:
                stock = Stock.objects.get(id=row['stock_id'])
                
                # Validate trade type
                trade_type = row['trade_type'].upper()
                if trade_type not in [Trade.BUY, Trade.SELL]:
                    raise ValueError(f"Invalid trade type: {trade_type}")
                
                # Validate quantity
                try:
                    quantity = int(row['quantity'])
                    if quantity <= 0:
                        raise ValueError("Quantity must be positive")
                except ValueError:
                    raise ValueError("Quantity must be a positive integer")
                
                trades.append(Trade(
                    user=request.user,
                    stock=stock,
                    trade_type=trade_type,
                    quantity=quantity,
                    price_at_trade=stock.price
                ))
                success_count += 1
                
            except Stock.DoesNotExist:
                errors.append(f"Row {row_num}: Stock {row.get('stock_id')} not found")
            except ValueError as e:
                errors.append(f"Row {row_num}: {str(e)}")
            except Exception as e:
                errors.append(f"Row {row_num}: Unexpected error - {str(e)}")
        
        if trades:
            try:
                with transaction.atomic():
                    Trade.objects.bulk_create(trades)
            except Exception as e:
                return Response(
                    {"error": f"Failed to create trades: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        response_data = {
            "created": success_count,
            "failed": len(errors),
            "total_rows_processed": len(reader.fieldnames) and (row_num - 1) or 0
        }
        
        if errors:
            response_data["errors"] = errors
        
        status_code = status.HTTP_201_CREATED if success_count else status.HTTP_400_BAD_REQUEST
        return Response(response_data, status=status_code)
    
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
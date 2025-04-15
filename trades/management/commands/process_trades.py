from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from trades.models import Stock, Trade
import csv
import os
from django.conf import settings
from datetime import datetime

class Command(BaseCommand):
    help = 'Process CSV files from the trades directory'
    
    def handle(self, *args, **options):
        User = get_user_model()
        directory = settings.TRADES_DIR
        
        if not os.path.exists(directory):
            os.makedirs(directory)
            self.stdout.write(self.style.WARNING(f"Created directory {directory}"))
            return
            
        processed_dir = os.path.join(directory, 'processed')
        if not os.path.exists(processed_dir):
            os.makedirs(processed_dir)
            
        for filename in os.listdir(directory):
            if filename.endswith('.csv'):
                filepath = os.path.join(directory, filename)
                try:
                    with open(filepath, 'r') as f:
                        reader = csv.DictReader(f)
                        trades = []
                        for row in reader:
                            try:
                                user = User.objects.get(id=row['user_id'])
                                stock = Stock.objects.get(id=row['stock_id'])
                                trade = Trade(
                                    user=user,
                                    stock=stock,
                                    trade_type=row['trade_type'].upper(),
                                    quantity=int(row['quantity']),
                                    price_at_trade=stock.price
                                )
                                trades.append(trade)
                            except (User.DoesNotExist, Stock.DoesNotExist, KeyError, ValueError) as e:
                                continue
                                
                        if trades:
                            Trade.objects.bulk_create(trades)
                            self.stdout.write(
                                self.style.SUCCESS(f"Processed {len(trades)} trades from {filename}")
                        else:
                            self.stdout.write(
                                self.style.WARNING(f"No valid trades found in {filename}"))
                            
                        # Archive the file
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        new_filename = f"{timestamp}_{filename}"
                        os.rename(filepath, os.path.join(processed_dir, new_filename))
                        
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"Error processing {filename}: {str(e)}"))
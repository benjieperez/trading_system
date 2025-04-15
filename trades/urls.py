from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TradeViewSet, StockViewSet

router = DefaultRouter()
router.register(r'trades', TradeViewSet, basename='trade')
router.register(r'stocks', StockViewSet, basename='stock')

urlpatterns = [
    path('', include(router.urls)),
]
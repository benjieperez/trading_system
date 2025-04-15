import factory
from django.contrib.auth import get_user_model
from trades.models import Stock, Trade

User = get_user_model()

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'password')

class StockFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Stock

    id = factory.Sequence(lambda n: f'STOCK{n}')
    name = factory.Faker('company')
    price = factory.Faker('pydecimal', left_digits=3, right_digits=2, positive=True)

class TradeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Trade

    user = factory.SubFactory(UserFactory)
    stock = factory.SubFactory(StockFactory)
    trade_type = 'BUY'
    quantity = factory.Faker('pyint', min_value=1, max_value=1000)
    price_at_trade = factory.SelfAttribute('stock.price')
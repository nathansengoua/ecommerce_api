from django.urls import path
from .views import health_check
from .views import protected_ping

urlpatterns = [
    path('ping/', protected_ping, name='protected_ping'),
    path('health/', health_check),
]

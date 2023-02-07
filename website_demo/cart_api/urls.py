from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from cart_api import views

urlpatterns = [
    path('cart/', views.CartList.as_view(), name='CartList'),
    # path('cart/<int:pk>', views.CartDetail.as_view(), name='CartDetail'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
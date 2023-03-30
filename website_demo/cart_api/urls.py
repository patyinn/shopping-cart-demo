from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from cart_api import views

urlpatterns = [
    path('cart/product/<str:product_id>/<str:class_name>/<str:app_name>', views.product_process, name='ProductDetail'),
    path('cart/', views.CartList.as_view(), name='CartList'),
    path('cart/<int:entry_id>', views.CartDetail.as_view(), name='CartDetail'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
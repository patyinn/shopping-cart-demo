from django.urls import path

from . import views

urlpatterns = [
    path('read/', views.CartView.read_cart, name='read_cart'),  # view cart items
    path('update/', views.CartView.update_cart, name='update_cart'),  # update cart items
    path('add/', views.CartView.add_cart, name='add_cart'),  # add merchandise to cart
    path('remove/', views.CartView.remove_cart, name='remove_cart'),  # remove merchandise from cart
]
from django.urls import path
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView
from .import views

urlpatterns = [
    path('', views.index, name='index'),
    path('categories/<str:mom>', views.category_page, name='category'),
    path('Entry/<str:child>', views.plant_page, name='plant_page'),
    path('AddCart/<str:product>', views.add_to_cart, name='add_to_cart'),
    path('RemoveItem/<str:product>', views.remove_from_cart, name='remove_cart'),
    path('UpdateCart/<str:product>', views.Update_cart, name='update_cart'),
    path('Cart', views.get_cart, name='Cart'),
    path('Order', views.order_page, name='Ordering'),
    path('OrderComplete/<str:id>', views.complete_page, name='Completion'),

    path("favicon.ico", RedirectView.as_view(url=staticfiles_storage.url("favicon.ico")))
]
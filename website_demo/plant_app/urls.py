from django.urls import path
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView
from .import views

urlpatterns = [
    path('', views.index, name='index'),
    path('categories/<str:mom>', views.category_page, name='category'),
    path('Entry/<str:child>', views.plant_page, name='plant_page'),
    path('AddCart/<str:product>', views.add_to_cart, name='add_to_cart'),
    path('RemoveItem/<int:item_pk>', views.remove_from_cart, name='remove_cart'),
    path('UpdateCart/<str:product>/<int:item_pk>', views.update_cart, name='update_cart'),
    path('Cart', views.get_cart, name='Cart'),
    path('Order', views.order_page, name='Ordering'),
    path('OrderComplete/<str:order_id>', views.complete_page, name='Completion'),

    path('accounts/login', views.login_page, name='Login'),
    path('accounts/registration', views.register_page, name='Registration'),
    path('accounts/logout', views.logout_page, name='Logout'),
    path('activate/<str:token>', views.activate_page, name='Activate'),

    path("favicon.ico", RedirectView.as_view(url=staticfiles_storage.url("favicon.ico")))
]
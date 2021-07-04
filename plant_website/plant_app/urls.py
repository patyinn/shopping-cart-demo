from django.urls import path
from .import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:id>', views.plant_page, name='page_plant'),
]
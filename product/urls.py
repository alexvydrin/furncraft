from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name='main'),
    path('products/', views.product_list, name='product_list'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('costs/', views.cost_list, name='cost_list'),
    path('import_main/', views.import_main, name='import_main'),
    path('import_pricelist/', views.import_pricelist, name='import_pricelist'),
]

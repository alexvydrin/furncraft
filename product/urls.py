from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name='main'),
    path('products/', views.product_list, name='product_list'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('costs/', views.cost_list, name='cost_list'),
    path('import_main/', views.import_main, name='import_main'),
    path('test_main/', views.test_main, name='test_main'),
    path('import_pricelist/', views.import_pricelist, name='import_pricelist'),
    path('import_product_calculation/', views.import_product_calculation, name='import_product_calculation'),
    path('import_cost/', views.import_cost, name='import_cost'),
    path('import_calculation/', views.import_calculation, name='import_calculation'),
    path('test_import_pricelist/', views.test_import_pricelist, name='test_import_pricelist'),
    path('test_import_product_calculation/', views.test_import_product_calculation, name='test_import_product_calculation'),
    path('test_import_cost/', views.test_import_cost, name='test_import_cost'),
    path('test_import_calculation/', views.test_import_calculation, name='test_import_calculation'),
    path('re_price_calc/', views.re_price_calc, name='re_price_calc'),
]

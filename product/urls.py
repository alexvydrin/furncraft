from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name='main'),
    path('products/', views.product_list, name='product_list'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('product_passport_file/<int:pk>/', views.product_passport_file, name='product_passport_file'),
    path('product_passport_test/<int:pk>/', views.product_passport_test, name='product_passport_test'),
    path('product_offer_file/<int:pk>/', views.product_offer_file, name='product_offer_file'),
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
    path('test_re_price_calc/', views.test_re_price_calc, name='test_re_price_calc'),
    path('test_total/', views.test_total, name='test_total'),
    path('test_site/', views.test_site, name='test_site'),
    path('import_site_link/', views.import_site_link, name='import_site_link'),
]

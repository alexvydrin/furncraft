from django.shortcuts import render, get_object_or_404
from .models import Product, Cost
from .unit_import import import_pricelist_code, import_cost_code,\
    test_import_pricelist_code, test_import_cost_code

# from django.utils import timezone


def main(request):
    return render(request, 'product/main.html')


def product_list(request):
    # products = Product.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    products = Product.objects.order_by('name')
    return render(request, 'product/product_list.html', {'products': products})


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'product/product_detail.html', {'product': product})


def cost_list(request):
    costs = Cost.objects.order_by('sort')
    return render(request, 'product/cost_list.html', {'costs': costs})


def import_main(request):
    return render(request, 'product/import_main.html')


def test_main(request):
    return render(request, 'product/test_main.html')


def import_pricelist(request):
    log = import_pricelist_code()
    return render(request, 'product/log_result.html', {'log': log})


def import_cost(request):
    log = import_cost_code()
    return render(request, 'product/log_result.html', {'log': log})


def test_import_pricelist(request):
    log = test_import_pricelist_code()
    return render(request, 'product/log_result.html', {'log': log})


def test_import_cost(request):
    log = test_import_cost_code()
    return render(request, 'product/log_result.html', {'log': log})

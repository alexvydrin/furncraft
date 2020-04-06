from django.shortcuts import render, get_object_or_404
from .models import Product, Cost, Calculation
from .unit_import import import_pricelist_code, import_cost_code, \
    import_calculation_code, \
    test_import_pricelist_code, test_import_cost_code


def main(request):
    return render(request, 'product/main.html')


def product_list(request):
    # products = Product.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    products = Product.objects.order_by('name')
    return render(request, 'product/product_list.html', {'products': products})


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    calculations = Calculation.objects.filter(product_id=pk)  # .order_by('cost_id.sort') - так не получается

    # Готовим таблицу для вывода
    items = []
    summ_total = 0
    for calculation in calculations:

        # Смотрим указано ли для данного изделия уточненная доля отходов
        if calculation.waste_percent:  # да, указано
            waste_percent_fact = calculation.waste_percent
            waste_percent_fact_for_table = calculation.waste_percent
        else:  # нет, не указано
            waste_percent_fact = calculation.cost_id.waste_percent
            waste_percent_fact_for_table = "="  # показываем в таблице, что уточненная доля отходов не указана

        summ = (calculation.cost_id.price or 0) * (1 + (waste_percent_fact or 0)) * (calculation.amount or 0)
        summ += calculation.cost_add or 0
        summ_total += summ

        item = {
            'name': calculation.cost_id.name,
            'price': calculation.cost_id.price,
            'waste_percent_plan': calculation.cost_id.waste_percent,
            'waste_percent_fact': waste_percent_fact_for_table,
            'amount': calculation.amount,
            'cost_add': calculation.cost_add,
            'sort': calculation.cost_id.sort,
            'summ': summ
        }
        items.append(item)

    return render(request, 'product/product_detail.html',
                  {'product': product, 'items': sorted(items, key=lambda x: x['sort'] or 0), 'summ_total': summ_total})


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


def import_calculation(request):
    log = import_calculation_code()
    return render(request, 'product/log_result.html', {'log': log})


def test_import_pricelist(request):
    log = test_import_pricelist_code()
    return render(request, 'product/log_result.html', {'log': log})


def test_import_cost(request):
    log = test_import_cost_code()
    return render(request, 'product/log_result.html', {'log': log})

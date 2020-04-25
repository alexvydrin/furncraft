from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Cost, Calculation
from .unit_import import \
    import_pricelist_code, test_import_pricelist_code, \
    import_product_calculation_code, test_import_product_calculation_code, \
    import_cost_code, test_import_cost_code, \
    import_calculation_code, test_import_calculation_code, \
    re_price_calc_code
from .unit_site import test_site_code


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
        waste_percent_plan_for_table = ""
        if calculation.cost_id.waste_percent:
            waste_percent_plan_for_table = f"{calculation.cost_id.waste_percent * 100:.0f}%"
        if calculation.waste_percent:  # да, указано
            waste_percent_fact = calculation.waste_percent
            waste_percent_fact_for_table = f"{calculation.waste_percent * 100:.0f}%"
        else:  # нет, не указано
            waste_percent_fact = calculation.cost_id.waste_percent
            if waste_percent_plan_for_table:
                waste_percent_fact_for_table = "="  # показываем в таблице, что уточненная доля отходов не указана
            else:
                waste_percent_fact_for_table = ""

        summ = (calculation.cost_id.price or 0) * (1 + (waste_percent_fact or 0)) * (calculation.amount or 0)
        summ += calculation.cost_add or 0
        summ_total += summ

        item = {
            'name': calculation.cost_id.name,
            'price': calculation.cost_id.price or "",
            'waste_percent_plan': waste_percent_plan_for_table,
            'waste_percent_fact': waste_percent_fact_for_table,
            'amount': calculation.amount or "",
            'cost_add': calculation.cost_add or "",
            'sort': calculation.cost_id.sort,
            'summ': summ
        }

        items.append(item)

    # коэффициент наценки для получения оптовой цены - цена со склада
    ratio_storage = 1.36
    # коэффициент наценки для получения розничной цены - цена в магазине
    ratio_shop = 1.4
    # общий коэффициент
    ratio = ratio_storage * ratio_shop
    price_shop = summ_total * ratio

    return render(request, 'product/product_detail.html',
                  {'product': product, 'items': sorted(items, key=lambda x: x['sort'] or 0),
                   'summ_total': summ_total, 'ratio': ratio, 'price_shop': price_shop})


def product_passport_file(request, pk):
    from .forms import ProductPassportfileForm
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        form = ProductPassportfileForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save(commit=False)

            name_for_test = product.passport_file.name  # ситуация при корректировке - для аккуратности
            if name_for_test and name_for_test[:11] == "passports /":
                name_for_test = name_for_test[11:]

            if name_for_test == f"Паспорт {product.name}.xlsx" or not product.passport_file:
                product.save()
                return redirect('product_list')
            else:
                log = \
                    [f"[{name_for_test}] - Выбран файл",
                     f"[Паспорт {product.name}.xlsx] - Нужен файл",
                     f"Загрузка файла отменена"]
                return render(request, 'product/log_result.html', {'log': log})
    else:
        form = ProductPassportfileForm(instance=product)

    return render(request, 'product/product_passport_file.html', {'product': product, 'form': form})


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


def import_product_calculation(request):
    log = import_product_calculation_code()
    return render(request, 'product/log_result.html', {'log': log})


def test_import_product_calculation(request):
    log = test_import_product_calculation_code()
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


def test_import_calculation(request):
    log = test_import_calculation_code()
    return render(request, 'product/log_result.html', {'log': log})


def re_price_calc(request):
    log = re_price_calc_code(mode="save")
    return render(request, 'product/log_result.html', {'log': log})


def test_re_price_calc(request):
    log = re_price_calc_code(mode="test")
    return render(request, 'product/log_result.html', {'log': log})


def test_total(request):
    log_total = [f"Все тесты - начало"]
    count_test = 0

    log = test_import_pricelist_code()
    del log[0]
    del log[-1]
    count_test += 1
    log_total += log

    log = test_import_product_calculation_code()
    del log[0]
    del log[-1]
    count_test += 1
    log_total += log

    log = test_import_cost_code()
    del log[0]
    del log[-1]
    count_test += 1
    log_total += log

    log = test_import_calculation_code()
    del log[0]
    del log[-1]
    count_test += 1
    log_total += log

    log = re_price_calc_code(mode="test")
    del log[0]
    del log[-1]
    count_test += 1
    log_total += log

    log_total.append(f"Все тесты - окончание. Выполнено тестов: {count_test}. Найдено ошибок: {len(log_total)-1}")
    return render(request, 'product/log_result.html', {'log': log_total})


def test_site(request):
    log = test_site_code(mode="test")
    return render(request, 'product/log_result.html', {'log': log})


def import_site_link(request):
    log = test_site_code(mode="import")
    return render(request, 'product/log_result.html', {'log': log})

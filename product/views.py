from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Cost, Calculation
from .unit_import import \
    import_pricelist_code, test_import_pricelist_code, \
    import_product_calculation_code, test_import_product_calculation_code, \
    import_cost_code, test_import_cost_code, \
    import_calculation_code, test_import_calculation_code, \
    re_price_calc_code
from .unit_site import test_site_code
from .unit_passport import get_amount_from_passport


def main(request):
    return render(request, 'product/main.html')


def product_list(request):
    # Определяем есть фильтр или нет
    if request.method == "POST":
        # здесь надо использовать фильтр

        products = Product.objects.order_by('name')

        name_substring = str(request.POST['name_substring'])
        name_endstring = str(request.POST['name_endstring'])

        str_filter = ""
        if name_substring:
            str_filter += f'фрагмент наименования = "{name_substring}" '
            products = products.filter(name__icontains=name_substring)
        if name_endstring:
            str_filter += f'окончание наименования = "{name_endstring}" '
            products = products.filter(name__iendswith=name_endstring)
        if not str_filter:
            str_filter = "все изделия"

    else:
        name_substring = ""
        name_endstring = ""
        str_filter = "все изделия"
        products = Product.objects.order_by('name')

    # считаем итоги с учетом фильтра
    count_products = products.count()
    count_passports = products.exclude(passport_file='').count()

    # TODO: при удалении файла счетчик продолжает считать его как не удаленный - непонятка
    # а у паспортов работает все нормально
    # вариант как у паспортов: count_offers =products.exclude(offer_file='').count() - не работает
    # count_offers = products.filter(offer_file__icontains='').count() # считает удаленные тоже
    # Попытаемся сделать медленно, но правильно
    # Сначала получим список всех изделий, затем в цикле проверим поле offer_file
    count_offers = 0
    for product in products:
        # print(f"product = {product.name} offer_file={product.offer_file}")
        if product.offer_file:
            count_offers += 1

    count_links = products.exclude(site_link='').count()

    return render(request, 'product/product_list.html', {'products': products,
                                                         'count_products': count_products,
                                                         'count_passports': count_passports,
                                                         'count_offers': count_offers,
                                                         'count_links': count_links,
                                                         'str_filter': str_filter,
                                                         'name_substring': name_substring,
                                                         'name_endstring': name_endstring,
                                                         })


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


def product_passport_test(request, pk):
    product = get_object_or_404(Product, pk=pk)
    calculations = Calculation.objects.filter(product_id=pk)

    log = []  # список ошибок, найденных в процессе тестирования

    # Готовим таблицу для вывода
    items = []
    for calculation in calculations:
        if calculation.amount:

            # TODO: заменить эту заглушку на признак в базе данных материалы/работы
            if calculation.cost_id.name.lower()[:6] in (
                    "сборка",
                    "распил",
                    "фрезер",
                    "поклей",
                    "резка",
                    "обрабо",
                    "пазовк",
                    "кромле"):
                continue

            item = {
                'name': calculation.cost_id.name,
                'amount': calculation.amount or "",
                'sort': calculation.cost_id.sort,
                'name_passport': "",
                'amount_passport': ""
            }
            items.append(item)

    # Получаем данные из паспорта
    items_passport = get_amount_from_passport(product.passport_file.name, log)

    for item_passport in items_passport:

        # Ищем совпадения простым перебором
        for item_iter in items:
            # минимальная длина для сравнения минус 1, тогда например "гвоздь" = "Гвозди толевые"
            min_len = min(len(item_iter["name"].strip()), len(item_passport["name"].strip())) - 1
            # сравниваем если длина не менее 3 символов, иначе возможны непонятки
            if min_len > 3 and\
                    item_iter["name"].strip().lower()[:min_len] == item_passport["name"].strip().lower()[:min_len]:
                item_iter['name_passport'] = item_passport["name"]
                try:
                    item_iter['amount_passport'] = round(item_passport["amount"], 2)
                except TypeError:
                    item_iter['amount_passport'] = item_passport["amount"]
                break
        else:  # Если не нашли соответствия
            item = {
                'name': "",
                'amount': "",
                'sort': 100500,  # TODO: максимальная + 1
                'name_passport': item_passport["name"]
            }

            try:
                item['amount_passport'] = round(item_passport["amount"], 2)
            except TypeError:
                item['amount_passport'] = item_passport["amount"]

            if item['amount_passport']:
                items.append(item)

    # TODO: расшифровывать все таблицы материалов в excel а не только ЛДСП
    # пока будем предупреждать о том что не все данные считываются
    for item in items:
        if not item['name_passport'] and item["name"].strip().lower() in\
                ("бронза", "двпо", "3 Д панель", "обложка", "мдф", "зеркало", "сатинат"):
            item['name_passport'] = "(пока не тестируется)"

    return render(request, 'product/product_passport_test.html',
                  {'product': product, 'items': sorted(items, key=lambda x: x['sort'] or 0), 'log': log})


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


def product_offer_file(request, pk):
    from .forms import ProductOfferfileForm
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        form = ProductOfferfileForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save(commit=False)

            name_for_test = product.offer_file.name  # ситуация при корректировке - для аккуратности
            if name_for_test and name_for_test[:8] == "offers /":
                name_for_test = name_for_test[8:]

            if name_for_test == f"КП {product.name}.jpg" or \
                    name_for_test == f"КП {product.name}.png" or \
                    not product.offer_file:
                product.save()
                return redirect('product_list')
            else:
                log = \
                    [f"[{name_for_test}] - Выбран файл",
                     f"[КП {product.name}.jpg] или [КП {product.name}.png] - Нужен файл",
                     f"Загрузка файла отменена"]
                return render(request, 'product/log_result.html', {'log': log})
    else:
        form = ProductOfferfileForm(instance=product)

    return render(request, 'product/product_offer_file.html', {'product': product, 'form': form})


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

    log_total.append(f"Все тесты - окончание. Выполнено тестов: {count_test}. Найдено ошибок: {len(log_total) - 1}")
    return render(request, 'product/log_result.html', {'log': log_total})


def test_site(request):
    log = test_site_code(mode="test")
    return render(request, 'product/log_result.html', {'log': log})


def import_site_link(request):
    log = test_site_code(mode="import")
    return render(request, 'product/log_result.html', {'log': log})

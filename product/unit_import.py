import openpyxl


def del_double_space(s):
    while "  " in s:
        s = s.replace("  ", " ")
    return s


def get_d_pricelist():

    f = r"static/data/Прайс Основной 2019октябрь_магазины.xlsx"

    d_pricelist = []

    wb = openpyxl.load_workbook(filename=f, read_only=False, data_only=True)

    ws = wb['прайс']
    rows = ws.max_row
    for c in range(4, 4 + 1):
        for r in range(5, rows + 1):
            name = ws.cell(row=r, column=3).value
            if not name or not isinstance(name, str):
                continue
            name = del_double_space(name.strip())

            # ищем до матрацев
            if name[:6].lower() == "матрац":
                break

            # подставляем метку серии в название
            type_product = "э"  # эко

            i_product = {
                'name': name + " " + type_product
            }

            # проверяем на повторение
            for i in d_pricelist:
                if i['name'] == i_product['name']:
                    break
            else:  # добавляем только уникальные позиции

                price_doc = ws.cell(row=r, column=c).value or 0

                if price_doc:
                    i_product['price_doc'] = price_doc
                    d_pricelist.append(i_product)

    return d_pricelist


def import_pricelist_code():

    log = [f"Импорт прайса - начало"]

    d_pricelist = get_d_pricelist()

    n_count_added = 0

    # добавляем данные в базу данных
    from product.models import Product
    from django.contrib.auth.models import User
    me = User.objects.get(username='alex')

    for i_pricelist in d_pricelist:
        name = i_pricelist['name']
        price_doc = i_pricelist['price_doc']
        if not len(Product.objects.filter(name=name)):
            Product.objects.create(author=me, name=name, price_doc=price_doc)
            n_count_added += 1

    log.append(f"Импорт окончен. Всего изделий в прайсе: {len(d_pricelist)}, из них импортировано: {n_count_added}")
    return log


def test_import_pricelist_code():
    """
        тестирование идентичности данных в прайслисте (файл эксель) и в базе данных
        проверяются следующие ошибки:
        1) в файле эксель есть изделие (name, price_doc), а в базе данных нет
        2) значение price_doc различается
        3) в базе данных есть изделие (name, price_doc), а в файле эксель нет
    """

    from product.models import Product

    log = [f"Тестирование идентичности данных в прайслисте (файл эксель) и в базе данных"]

    d_pricelist = get_d_pricelist()

    n_count = 0

    for i_pricelist in d_pricelist:
        name = i_pricelist['name']
        if not len(Product.objects.filter(name=name)):
            log.append(f"Ошибка: В файле эксель есть изделие, а в базе данных нет: {name}")
            n_count += 1
            continue
        price_doc = i_pricelist['price_doc']
        i_product = Product.objects.get(name=name)
        if price_doc != i_product.price_doc:
            log.append(f"Ошибка: В файле эксель цена = {price_doc}, а в базе данных цена = {i_product.price_doc}:"
                       f" {name}")
            n_count += 1

    products = Product.objects.all()
    for i_product in products:
        name = i_product.name
        # ищем простым перебором
        for i_pricelist in d_pricelist:
            if i_pricelist['name'] == name:
                break
        else:
            log.append(f"Ошибка: В базе данных есть изделие, а в файле эксель нет: {name}")
            n_count += 1

    log.append(f"Тестирование окончено. Всего ошибок найдено: {n_count}")
    return log

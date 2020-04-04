import openpyxl
# import json


def del_double_space(s):
    while "  " in s:
        s = s.replace("  ", " ")
    return s


def import_pricelist_code():

    log = [f"Импорт прайса - начало"]

    f = r"static/data/Прайс Основной 2019октябрь_магазины.xlsx"

    d_price = []
    n_count = 0

    wb = openpyxl.load_workbook(filename=f, read_only=False, data_only=True)

    ws = wb['прайс']
    rows = ws.max_row
    for c in range(4, 4 + 1):
        for r in range(5, rows+1):
            name_product = ws.cell(row=r, column=3).value
            if not name_product or not isinstance(name_product, str):
                continue
            name_product = del_double_space(name_product.strip())

            # ищем до матрацев
            if name_product[:6].lower() == "матрац":
                break

            # подставляем метку серии в название
            type_product = "эко"

            i_product = {
                'type_product': type_product,
                'name_product': name_product
            }
            # проверяем на повторение
            for i in d_price:
                if i['name_product'] == i_product['name_product'] and i['type_product'] == i_product['type_product']:
                    break
            else:  # добавляем только уникальные позиции

                price = ws.cell(row=r, column=c).value or 0

                if price:
                    i_product['price'] = price
                    d_price.append(i_product)
                    n_count += 1

                log.append(f"{i_product['name_product']}")

        log.append(f"Импорт прайса закончен")

        # вывод результата
        # with open("db_d_price.json", "w") as write_file:
        #    json.dump(d_price, write_file, ensure_ascii=False)

        log.append(f"Импорт окончен. Всего импортировано строк прайса: {n_count}")
        return log

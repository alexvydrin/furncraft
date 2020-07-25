# Модуль для работы с сайтом

from bs4 import BeautifulSoup
import requests as req


def test_site_code(mode='test'):

    if mode == 'import':
        log = [f"Импорт с сайта ссылок на изделия  - начало"]
    else:
        log = [f"Тестирование идентичности изделий на сайте и в базе данных"]

    page = 1
    links = []
    first_name = ""

    while True:

        site = f"https://komfortm.ru/catalog/"
        if page > 1:
            site += f"?PAGEN_1={page}"

        resp = req.get(site)

        soup = BeautifulSoup(resp.text, 'lxml')

        for tag in soup.find_all("div", {'class': 'product-info text-left'}):
            tag_price = tag.find("div", {'class': 'product-price'}).span.meta.get('content')
            name = f"{tag.h2.a.text}".strip()
            if not first_name:
                first_name = name
            else:
                if first_name == name:  # признак что листание страниц закончено на сайте
                    page = -1
                    break
            price = f"{tag_price}".strip()
            if price:
                price = float(price)
            else:
                price = 0.0
            link = {
                'name': name,
                'href': f"https://komfortm.ru{tag.h2.a.get('href')}",
                'price': price
            }
            links.append(link)

        if page < 0:  # признак что листание страниц закончено на сайте
            break

        if page > 999:  # на всякий случай выход для устранения зацикливания
            break

        page += 1

    # for link in sorted(links, key=lambda x: x['name']):
    #    log.append(f"{link['name']} = {link['price']}")

    """
        тестирование идентичности данных на сайте и в базе данных
        проверяются следующие ошибки:
        1) на сайте есть изделия, а в базе данных нет
        2) значение price_doc различается
        3) ссылка на изделие в базе данных неправильное - при необходимости нужно исправить (спец.режим)
        4) в базе данных есть изделие, а на сайте нет
    """

    from product.models import Product

    n_count = 0
    n_count_added = 0

    for link in links:
        name = link['name']

        if name[-2:].lower() == ' э' or name[-2:].lower() == ' л':
            # пока только эко и лайт
            pass
        else:
            # остальные наименования не рассматриваем
            continue

        # if not len(Product.objects.filter(name=name)):
        if not len(Product.objects.filter(name__iexact=name)):
            log.append(f"Ошибка: На сайте есть изделие, а в базе данных нет: {name}")
            n_count += 1
            continue

        price_site = link['price']
        href_site = link['href']

        # i_product = Product.objects.get(name=name)
        i_product = Product.objects.get(name__iexact=name)
        if price_site != i_product.price_doc:
            log.append(f"Ошибка: На сайте цена = {price_site}, а в базе данных цена = {i_product.price_doc}:"
                       f" {name}")
            n_count += 1

        if href_site != i_product.site_link:

            if mode == 'import':
                if not i_product.site_link:
                    i_product.site_link = href_site
                    i_product.save()
                    n_count_added += 1
            else:
                log.append(f"Ошибка: На сайте адрес = {href_site}, а в базе данных ссылка = {i_product.site_link}:"
                           f" {name}")
                n_count += 1

    if mode == 'import':
        pass  # при импорте эти ошибки не проверяем, только при тестировании
    else:
        products = Product.objects.all()
        for i_product in products:

            # сравниваем только изделия с фактической (задокументированной) ценой
            # и если в базе данных для изделия сушествует коммерческое предложение
            if i_product.price_doc is None:
                continue
            if not i_product.offer_file:
                continue

            name = i_product.name
            # ищем простым перебором
            for link in links:
                if link['name'] == name:
                    break
            else:
                log.append(f"Ошибка: В базе данных есть изделие, а на сайте нет: {name}")
                n_count += 1

    if mode == 'import':
        log.append(f"Импорт окончен. Всего изделий на сайте: {len(links)}, ссылок импортировано: {n_count_added}")
    else:
        log.append(f"Тестирование окончено. Всего ошибок найдено: {n_count}")

    return log

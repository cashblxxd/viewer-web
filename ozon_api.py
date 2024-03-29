import requests
import json
from pprint import pprint
import csv
import time
from datetime import datetime, timedelta
from zipfile import ZipFile
import dateutil.relativedelta
from json import load, dump
from PyPDF2 import PdfFileMerger
import os


def get_items_ids(shop_api_key, client_id, state='ALL'):
    print("Getting ids...")
    headers = {
        'Client-Id': str(client_id),
        'Api-Key': shop_api_key,
        'Content-Type': 'application/json'
    }
    payload = "{\n  \"filter\": {\n    \"visibility\": \"" + state + "\"\n  },\n  \"page\": 1,\n  \"page_size\": 1000\n}"
    r = requests.post(url="http://api-seller.ozon.ru/v1/product/list", headers=headers, data=payload)
    return r.json()


def get_product_parameters(product_id, offer_id, shop_api_key, client_id):
    headers = {
        'Client-Id': str(client_id),
        'Api-Key': shop_api_key,
        'Content-Type': 'application/json'
    }
    payload = {
        "filter": {
            "offer_id": offer_id,
            "product_id": product_id
        }
    }
    return requests.post(url="http://api-seller.ozon.ru/v2/products/info/attributes", headers=headers, json=payload).json()


def get_sku(r):
    fbo, fbs = "", ""
    for i in r.get("sources", []):
        if i["source"] == "fbo":
            fbo = i["sku"]
        elif i["source"] == "fbs":
            fbs = i["sku"]
    return {
        "fbo": fbo,
        "fbs": fbs
    }


def get_item_state(state):
    if state == "": return ""
    if state == "processing": return "Информация о товаре добавляется в систему, ожидайте"
    if state == "moderating": return "Товар проходит модерацию, ожидайте"
    if state == "processed": return "Информация обновлена"
    if state == "failed_moderation": return "Товар не прошел модерацию"
    if state == "failed_validation": return "Товар не прошел валидацию"
    if state == "failed": return "Возникла неизвестная ошибка"
'''"Ширина, мм": str(params.get("width", "")).replace(".", ","),
		"Высота, мм": str(params.get("height", "")).replace(".", ","),
		"Глубина, мм": str(params.get("depth", "")).replace(".", ","),'''


def parse_date_short(s):
    #print(s)
    if not s:
        return "-"
    date = datetime.strptime(s, '%Y-%m-%dT%H:%M:%SZ')
    return date.strftime('%d-%m-%Y %H:%M:%S')


def parse_date_long(s):
    if not s: return ""
    date = datetime.strptime(s, '%Y-%m-%dT%H:%M:%S.%fZ')
    return date.strftime('%H:%M:%S %d-%m-%Y')


def get_item_info(product_id, offer_id, shop_api_key, client_id):
    headers = {
        'Client-Id': str(client_id),
        'Api-Key': shop_api_key,
        'Content-Type': 'application/json'
    }
    payload = {
        "offer_id": offer_id,
        "product_id": product_id
    }
    r = requests.post(url="http://api-seller.ozon.ru/v2/product/info", headers=headers, json=payload).json()["result"]
    #arams = get_product_parameters(product_id, offer_id, shop_api_key, client_id)
    #sku_ids = get_sku(r)
    """
        Артикул 
Баркод 
Наименование 
Статус 
видимость на сайте 
Доступно на складе 
Текущая цена
'''
        "Ozon Product ID": product_id,
        "FBO OZON SKU ID": sku_ids["fbo"],
        "FBS OZON SKU ID": sku_ids["fbs"],
        
        
        
        
        "Дата создания": parse_date_long(r.get("created_at", "")),
        
        
        "Цена до скидки (перечеркнутая цена), руб.": str(r.get("old_price", "")).replace(".", ","),
        "Цена Premium, руб.": str(r.get("premium_price", "")).replace(".", ","),
        "Рыночная цена, руб.": str(r.get("recommended_price", "")).replace(".", ","),
        "Размер НДС, %": {"": "0", "0.000000": "0", "0.100000": "10%", "0.200000": "20%", }[str(r.get("vat", "0"))]'''
    """
    result = {
        "Артикул": offer_id,
        "Баркод": r["barcode"],
        "Наименование": r["name"],
        "Статус": get_item_state(r.get("state", "-")),
        "Картинка": r["images"],
        "Видимость на сайте": "да" if r.get("visible", 0) else "нет",
        "Доступно на складе, шт": r.get("stocks", {}).get("present", "-"),
        "Текущая цена с учетом скидки, руб.": r.get("price", "-")
    }
    return result


def get_items_info(shop_api_key, client_id, status="ALL"):
    init_time = time.time()
    print("Getting items...")
    id_list = get_items_ids(shop_api_key, client_id, status)["result"]["items"]
    print("Got", len(id_list), "items in:", str(time.time() - init_time), "s")
    items = []
    for item in id_list:
        product_id, offer_id = item["product_id"], item["offer_id"]
        items.append(get_item_info(product_id, offer_id, shop_api_key, client_id))
        print("+" + str(time.time() - init_time), "s")
    print("Got in:", str(time.time() - init_time), "s")
    return items


def get_all_items(shop_api_key, client_id, uid):
    path = f'./{uid}'
    if not os.path.isdir(path):
        os.mkdir(path)
    for i in ["ALL", "VISIBLE", "INVISIBLE", "READY_TO_SUPPLY", "STATE_FAILED"]:
        items = get_items_info(shop_api_key, client_id, i)
        with open(f"{uid}/items_{i}.json", 'w+', encoding='utf-8') as f:
            dump(items, f, indent=4, ensure_ascii=False)
        print(i, 'done.')
    print("DONE")


def dump_items_csv(shop_api_key, client_id, name):
    print("Dumping to", name + "_" + str(datetime.now()) + '_products.csv')
    employee_data = get_items_info(shop_api_key, client_id)
    client_id = str(client_id)
    filename = name + "_" + '_products.csv'
    data_file = open(filename, 'w+', encoding='utf-8-sig', newline='')
    csv_writer = csv.writer(data_file, delimiter=';')
    count = 0
    for emp in employee_data:
        if count == 0:
            header = emp.keys()
            csv_writer.writerow(header)
            count += 1
        csv_writer.writerow(emp.values())
    data_file.close()
    print("Dumped successfully.")


def get_postings_list(shop_api_key, client_id, status=None):
    print("Getting postings list...")
    init_time = time.time()
    headers = {
        'Client-Id': str(client_id),
        'Api-Key': shop_api_key,
        'Content-Type': 'application/json'
    }
    payload = {
        "dir": "desc",
        "filter": {
            "since": ((datetime.now() + dateutil.relativedelta.relativedelta(months=-1)).replace(day=1)).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + "Z",
            "to": (datetime.now()).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + "Z"
        },
        "limit": 50,
        "offset": 0,
        "with": {
            "barcodes": False
        }
    }
    if status:
        payload["filter"]["status"] = status
    postings = []
    r = requests.post(url="http://api-seller.ozon.ru/v2/posting/fbs/list", headers=headers, json=payload).json()["result"]
    while r:
        postings.extend(r)
        payload["offset"] += 50
        #print("Offset:", payload["offset"], "time:", str(time.time() - init_time), "s")
        r = requests.post(url="http://api-seller.ozon.ru/v2/posting/fbs/list", headers=headers, json=payload).json()["result"]
    print("Got", len(postings), "in:", str(time.time() - init_time), "s")
    #pprint(postings)
    return postings


def get_posting_status(s):
    if s == "": return ""
    if s == "awaiting_packaging": return "Ожидает упаковки"
    if s == "not_accepted": return "Не принят в сортировочном центре"
    if s == "arbitration": return "Ожидает решения спора"
    if s == "awaiting_deliver": return "Ожидает отгрузки"
    if s == "delivering": return "Доставляется"
    if s == "driver_pickup": return "У водителя"
    if s == "delivered": return "Доставлено"
    if s == "cancelled": return "Отменено"


def get_sum(price_str, q_str):
    if not (price_str and q_str): return ""
    return str(float(price_str) * float(q_str))


def get_details(products):
    return '\n'.join(f'{product.get("quantity", "-")} шт. Артикул: {product.get("offer_id", "-")} {product.get("name", "-")}' for product in products)


def get_product_image(sku, shop_api_key, client_id):
    #print("Getting image for", sku, end="... ")
    try:
        headers = {
            'Client-Id': str(client_id),
            'Api-Key': shop_api_key,
            'Content-Type': 'application/json'
        }
        payload = {
            "sku": sku,
        }
        r = requests.post(url="http://api-seller.ozon.ru/v2/product/info", headers=headers, json=payload).json()["result"]
        #print("Success")
        return r["images"][0]
    except Exception as e:
        #print("Failed: ", e)
        return "https://image.flaticon.com/icons/png/512/1602/1602620.png"


def get_prices_sum(products):
    summ = 0
    for product in products:
        s = product.get("price", "-")
        if s != '-':
            summ += float(s)
    return str(summ)


def get_posting_info(r, shop_api_key, client_id, status=None):
    products = r.get("products", [{}])
    #pprint(r)
    #pprint(product)
    result = {
        "Принят в обработку": parse_date_short(r.get("in_process_at", "-")),
        "Номер заказа": r.get("order_number", "-"),
        "Номер отправления": r.get("posting_number", "-"),
        "Детали отправления": get_details(products),
        "Картинка": [get_product_image(products[i].get("sku", "-"), shop_api_key, client_id)
                     for i in range(len(products))],
        "Стоимость": get_prices_sum(products),
        # Стоимость !!!!!!!!!!!!!!!!!!
        "Дата отгрузки": parse_date_short(r.get("shipment_date", "-")),
    }
    if status == "awaiting_packaging":
        result["origin"] = r
    return result


def deliver_selected_postings(shop_api_key, client_id, uid, posting_numbers):
    try:
        with open(f"{uid}/postings_" + str(uid) + '_awaiting_packaging.json', 'r+', encoding='utf-8') as f:
            s = load(f)
    except Exception:
        return
    numbers = set(posting_numbers)
    postings = set()
    for posting in s:
        if posting["origin"]["posting_number"] in numbers:
            headers = {
                'Client-Id': str(client_id),
                'Api-Key': shop_api_key,
                'Content-Type': 'application/json'
            }
            payload = {
                "packages": [{"items": [
                    {
                        "quantity": i["quantity"],
                        "sku": i["sku"]
                    } for i in posting["origin"]["products"]
                ]}],
                "posting_number": posting["origin"]["posting_number"]
            }
            r = requests.post(url="http://api-seller.ozon.ru/v2/posting/fbs/ship", headers=headers, json=payload).json()
            if "result" in r:
                postings.add(posting["origin"]["posting_number"])
    awaiting_deliver = [i for i in s if i["origin"]["posting_number"] in postings]
    s = [i for i in s if i["origin"]["posting_number"] not in postings]
    for i in range(len(awaiting_deliver)):
        awaiting_deliver[i].pop("origin")
    try:
        with open(f"{uid}/postings_" + str(uid) + '_awaiting_packaging.json', 'w+', encoding='utf-8') as f:
            dump(s, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(e)
    s = []
    try:
        with open(f"{uid}/postings_" + str(uid) + '_awaiting_deliver.json', 'r+', encoding='utf-8') as f:
            s = load(f)
    except Exception as e:
        print(e)
    try:
        with open(f"{uid}/postings_" + str(uid) + '_awaiting_deliver.json', 'w+', encoding='utf-8') as f:
            dump(awaiting_deliver + s, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(e)


def get_postings_info(shop_api_key, client_id, uid='-', status=None):
    #print("Starting...")
    s = []
    print(((datetime.now() + dateutil.relativedelta.relativedelta(months=-1)).replace(day=1)))
    try:
        with open(f"{uid}/postings_" + str(uid) + f'{"_" + status if status else ""}.json', 'r+', encoding='utf-8') as f:
            s = load(f)
    except Exception as e:
        print(e)
    try:
        print("s:", len(s))
    except Exception as e:
        print(e)
    d = set()
    postings_list = get_postings_list(shop_api_key, client_id, status)
    actual_posting_numbers = set(i["posting_number"] for i in postings_list)
    s = [i for i in s if datetime.strptime(i["Принят в обработку"], '%d-%m-%Y %H:%M:%S') >= ((datetime.now() + dateutil.relativedelta.relativedelta(months=-1)).replace(day=1)) and i["Номер отправления"] in actual_posting_numbers]
    for i in s:
        d.add(i["Номер отправления"])
    postings_add = [get_posting_info(i, shop_api_key, client_id, status) for i in [i for i in postings_list if i["posting_number"] not in d]]
    #pprint(postings_add)
    #print("Done")
    result = postings_add + s
    return result


def get_postings_info_awaiting_packaging(shop_api_key, client_id, uid='-'):
    return get_postings_info(shop_api_key, client_id, uid, status='awaiting_packaging')


def get_postings_info_awaiting_deliver(shop_api_key, client_id, uid='-'):
    return get_postings_info(shop_api_key, client_id, uid, status='awaiting_deliver')


def get_postings_info_arbitration(shop_api_key, client_id, uid='-'):
    return get_postings_info(shop_api_key, client_id, uid, status='arbitration')


def get_postings_info_delivering(shop_api_key, client_id, uid='-'):
    return get_postings_info(shop_api_key, client_id, uid, status='delivering')


def get_postings_info_delivered(shop_api_key, client_id, uid='-'):
    return get_postings_info(shop_api_key, client_id, uid, status='delivered')


def get_postings_info_cancelled(shop_api_key, client_id, uid='-'):
    return get_postings_info(shop_api_key, client_id, uid, status='cancelled')


def print_acts(shop_api_key, client_id, user_id):
    headers = {
        'Client-Id': str(client_id),
        'Api-Key': shop_api_key,
        'Content-Type': 'application/json'
    }
    payload = {}
    r = requests.post(url="http://api-seller.ozon.ru/v2/posting/fbs/act/create", headers=headers, json=payload).json()
    pprint(r)
    try:
        res_id = r["result"]["id"]
    except Exception as e:
        print(e)
        return (False,)
    ready = False
    for i in range(100):
        headers = {
            'Client-Id': str(client_id),
            'Api-Key': shop_api_key,
            'Content-Type': 'application/json'
        }
        payload = {
            "id": res_id
        }
        r = requests.post(url="http://api-seller.ozon.ru/v2/posting/fbs/act/check-status",
                          headers=headers, json=payload).json()["result"]["status"]
        if r == "error":
            return (False,)
        if r == "ready":
            ready = True
            break
        time.sleep(2)
    if ready:
        headers = {
            'Client-Id': str(client_id),
            'Api-Key': shop_api_key,
            'Content-Type': 'application/json'
        }
        payload = {
            "id": res_id
        }
        r = requests.post(url="http://api-seller.ozon.ru/v2/posting/fbs/act/get-pdf", headers=headers, json=payload)
        with open(f'./{user_id}/Акт {datetime.now().strftime("%H:%M:%S %d.%m.%Y")}.pdf', 'wb') as f:
            f.write(r.content)


def get_markings(shop_api_key, client_id, posting_numbers, user_id):
    print("getting:", posting_numbers)
    filenames = []
    for i in range(len(posting_numbers)):
        headers = {
            'Client-Id': str(client_id),
            'Api-Key': shop_api_key,
            'Content-Type': 'application/json'
        }
        payload = {
            "posting_number": [posting_numbers[i]],
        }
        r = requests.post(url="http://api-seller.ozon.ru/v2/posting/fbs/package-label", headers=headers, json=payload)
        try:
            s = r.json()
            if s["error"]["code"] == "POSTINGS_NOT_READY":
                print("fuck i failed")
                print(s["error"]["message"])
                continue
        except Exception:
            pass
        filename = str(client_id) + "_" + str(i) + ".pdf"
        filenames.append(filename)
        with open(filename, 'wb') as f:
            f.write(r.content)
    merger = PdfFileMerger()

    for pdf in filenames:
        merger.append(pdf)
    print("here")
    path = f'./{user_id}'
    if not os.path.isdir(path):
        os.mkdir(path)
    merger.write(path + f"/Маркировки {datetime.now().strftime('%H:%M:%S %d.%m.%Y')}.pdf")
    merger.close()
    for file in filenames:
        os.remove(file)
    return (True,)


def dump_postings_csv(shop_api_key, client_id, name):
    print("Dumping to", name + "_" + str(datetime.now()) + '_postings.csv')
    employee_data = get_postings_info(shop_api_key, client_id)
    client_id = str(client_id)
    filename = name + "_" + '_postings.csv'
    data_file = open(filename, 'w+', encoding='utf-8-sig', newline='')
    csv_writer = csv.writer(data_file, delimiter=';')
    count = 0
    for emp in employee_data:
        if count == 0:
            header = emp.keys()
            csv_writer.writerow(header)
            count += 1
        csv_writer.writerow(emp.values())
    data_file.close()
    print("Dumped successfully.")

keys = {}

def load_keys():
    print("Loading keys...")
    with open('keys.csv', encoding='utf-8-sig') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        count = 0
        for row in reader:
            if not count:
                count += 1
                continue
            name, shop_api_key, client_id = row
            keys[name] = {
                "shop_api_key": shop_api_key,
                "client_id": client_id,
            }
    print("Loaded.")

def dump_all_items():
    init_time = time.time()
    print("Dumping items...")
    for i in keys:
        try:
            start_time = time.time()
            print("Start:", start_time)
            dump_items_csv(keys[i]["shop_api_key"], keys[i]["client_id"], i)
            print(i, "--- %s seconds ---" % (time.time() - start_time))
        except Exception as e:
            print(e)
    print("Total items:", str(time.time() - init_time))
    print("Finished dumping items.")

def dump_all_postings():
    init_time = time.time()
    print("Dumping postings...")
    for i in keys:
        try:
            start_time = time.time()
            print("Start:", start_time)
            dump_postings_csv(keys[i]["shop_api_key"], keys[i]["client_id"], i)
            print(i, "--- %s seconds ---" % (time.time() - start_time))
        except Exception as e:
            print(e)
    print("Total postings:", str(time.time() - init_time))
    print("Finished dumping postings.")

def dump_all_markets():
    print("Initializing...")
    load_keys()
    print("Keys:")
    pprint(keys)
    print("==============")
    dump_all_items()
    dump_all_postings()

    print("Done.")
'''
start_time = time.time()
dump_items_csv("ff33baac-ec9e-4925-852c-c6a2fca38565", 49268)
print("--- %s seconds ---" % (time.time() - start_time))'''
#load_keys()
#dump_postings_csv("ff33baac-ec9e-4925-852c-c6a2fca38565", 49268, 'test')
#dump_all_markets()
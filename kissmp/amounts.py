import json


DEFAULT_FEE= 1000
BILLION= 1000000000
TRILLION= 1000000000000

PAYMENT= 1000
DEPOSIT= 250	# buyer's and seller's deposit size
EXTRA= 50	# seller's penalty size if cancelled.


def amounts_buyer_create(price: float, fee: int, verbosity: bool= False) -> dict:
    amount = {
        'fee': fee,
        'price': price,
        'price_kmojos': int(float(price) * BILLION),
    }
    amount['buyer_amount'] = amount['price_kmojos'] * (PAYMENT + DEPOSIT)
    amount['seller_amount'] = amount['price_kmojos'] * (DEPOSIT + EXTRA)
    assert (price == float(amount['price_kmojos'])/BILLION),"Something wrong with price value: {0} != {1}".format(price, float(amount['price_kmojos'])/BILLION)
    if verbosity:
        print(f"amounts: {json.dumps(amount, indent=4)}")
    return amount

def amounts_seller_confirm(file: dict, fee: int, verbosity: bool= False) -> dict:
    amount = {
        'fee': fee,
        'old': file['price_kmojos'] * (PAYMENT + DEPOSIT),
        'deposit': file['price_kmojos'] * DEPOSIT,
        'penalty': file['price_kmojos'] * EXTRA,
    }
    amount['contribution'] = amount['deposit'] + amount['penalty']
    amount['new'] = amount['old'] + amount['contribution']
    if verbosity:
        print(f"amounts: {json.dumps(amount, indent=4)}")
    return amount

def amounts_buyer_finish(file: dict, fee: int, verbosity: bool= False) -> dict:
    amount = {
        'fee': fee,
        'old': file['price_kmojos'] * (PAYMENT + DEPOSIT + DEPOSIT + EXTRA),
        'buyer_deposit': file['price_kmojos'] * DEPOSIT,
        'seller_deposit': file['price_kmojos'] * (DEPOSIT + EXTRA),
        'new': 0,
    }
    if verbosity:
        print(f"amounts: {json.dumps(amount, indent=4)}")
    return amount

def amounts_buyer_cancel(file: dict, fee: int, verbosity: bool= False) -> dict:
    amount = {
        'fee': fee,
        'old': file['price_kmojos'] * (PAYMENT + DEPOSIT),
        'deposit': file['price_kmojos'] * DEPOSIT,
        'new': 0,
    }
    if verbosity:
        print(f"amounts: {json.dumps(amount, indent=4)}")
    return amount

def amounts_seller_cancel(file: dict, fee: int, verbosity: bool= False) -> dict:
    amount = {
        'fee': fee,
        'old': file['price_kmojos'] * (PAYMENT + DEPOSIT + DEPOSIT + EXTRA),
        'deposit': file['price_kmojos'] * DEPOSIT,
        'penalty': file['price_kmojos'] * EXTRA,
        'new': 0,
    }
    if verbosity:
        print(f"amounts: {json.dumps(amount, indent=4)}")
    return amount

def amounts_submit_review(fee: int, verbosity: bool= False) -> dict:
    amount = {
        'fee': fee,
        'treasury': 2000000000,
    }
    if verbosity:
        print(f"amounts: {json.dumps(amount, indent=4)}")
    return amount



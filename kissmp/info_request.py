import json
import requests

from chia.util.byte_types import hexstr_to_bytes
from chia.wallet.puzzles.p2_delegated_puzzle_or_hidden_puzzle import puzzle_for_synthetic_public_key
from kissmp.wallet_rpc import get_network
from kissmp.kissmp_drivers import (
    create_review_puzzle,
)


#API_ENDPOINT= "https://localhost:8484/"
API_ENDPOINT= "https://api.kissmy.parts:8484/"

def analyze_response(
    file: dict,
    data: json,
    verbosity: bool,
):
    buyer_cash_out_ph= '0x'+ str(puzzle_for_synthetic_public_key(hexstr_to_bytes(file['buyer_cupkey'])).get_tree_hash())

    if verbosity:
        print(f"response: {json.dumps(data, indent=4)}")
        #print(f"response: {data}")
        #print(f"response: {data['c_ph']}")
    if data['m_created'] == 0:
        print(f"payment from buyer not yet on chain.")
    elif data['m_spent'] == 0:
        print(f"payment waiting for seller to lock, so trade can begin.")
    elif data['c_ph'] != file['ph']:
        print(f"payment cancelled by buyer, nothing to do here.")
    elif data['c_spent'] == 0:
        print(f"payment locked by seller, waiting for buyer to confirm recieved goods.")
    elif (5.3 * data['gc_amount0']) > (data['gc_amount1']) and (5 * data['gc_amount0']) < (data['gc_amount1']) and data['gc_ph0'] == buyer_cash_out_ph:
        print(f"payment finished ok. nothing to do here.")
    elif (5.3 * data['gc_amount1']) > (data['gc_amount0']) and (5 * data['gc_amount1']) < (data['gc_amount0']) and data['gc_ph1'] == buyer_cash_out_ph:
        print(f"payment finished ok. nothing to do here.")
    else:
        print(f"payment cancelled by seller.")

def show_payment_info(
    file: dict,
    verbosity: bool,
):
    # amounts
    amount = {
        'price': "%.12f XCH" % (file['price_kmojos'] * 1000 / 1000000000000),
        'buyer_deposit': "%.12f XCH" % (file['price_kmojos'] * 250 / 1000000000000),
        'buyer_deposit_plus_payment': "%.12f XCH" % (file['price_kmojos'] * 1250 / 1000000000000),
        'buyer_deposit_plus_payment_plus_extra': "%.12f XCH" % (file['price_kmojos'] * 1300 / 1000000000000),
        'seller_deposit': "%.12f XCH" % (file['price_kmojos'] * 300 / 1000000000000),
        'seller_deposit_minus_penalty': "%.12f XCH" % (file['price_kmojos'] * 250 / 1000000000000),
        'seller_deposit_plus_payment': "%.12f XCH" % (file['price_kmojos'] * 1300 / 1000000000000),
        'full': "%.12f XCH" % (file['price_kmojos'] * 1550 / 1000000000000),
    }
    if verbosity:
        print(f"amounts: {json.dumps(amount, indent=4)}")
    else:
        print(f"Price: {amount['price']}")

    # request
    print(f"can take up to 10 seconds..")
    try:
        inputs = {}
        response1 = requests.get(API_ENDPOINT + "info/" + file['name'], json=inputs)
    except requests.ConnectionError:
        present_network= get_network()
        print(f"Error on request. Can not connect.")
        print(f"\nOriginal paymemt coin and child coin at https://xchscan.com/txns/{file['name']}")
        if "mainnet" != present_network:
            print(f"IF YOU WERE ON MAINNET, THAT YOU ARE NOT!!.->{present_network}")
        print(f"If there is no coin, maybe transaction didn't go through.")
        print(f"If it has not Child Coin and {amount['buyer_deposit_plus_payment']}, payment is waiting for seller to confirm trade.")
        print(f"If it has a Child Coin and {amount['full']}, seller started trade and waiting for buyer to receive and finish trade.")
        print(f"If Child coin has been cancel by seller, seller should have {amount['seller_deposit_minus_penalty']}, and buyer {amount['buyer_deposit_plus_payment_plus_extra']}.")
        print(f"If Child coin has been finished by buyer, seller should have {amount['seller_deposit_plus_payment']}, and buyer {amount['buyer_deposit']}.")
        return
    analyze_response(file, response1.json(), verbosity)


def show_review_info(cupkey: str, verbosity: bool):
    # Get puzzles
    positive_ph = '0x'+str(create_review_puzzle(1, hexstr_to_bytes(cupkey)).get_tree_hash())
    negative_ph = '0x'+str(create_review_puzzle(0, hexstr_to_bytes(cupkey)).get_tree_hash())
    if verbosity:
        print(f"positive_puzzlehash: {positive_ph}")
        print(f"negative_puzzlehash: {negative_ph}")
    #print(f"can take up to 10 seconds.")
    print(f"..")
    # request
    #inputs = {"operation": "CREATE", "expireDate": expire_date}
    try:
        inputs = {}
        response1 = requests.get(API_ENDPOINT + "stars/" + positive_ph, json=inputs)
        response2 = requests.get(API_ENDPOINT + "stars/" + negative_ph, json=inputs)
    except requests.ConnectionError:
        print(f"Error on request.")
        return
    # stars
    positive_stars= response1.json()[0]
    negative_stars= response2.json()[0]
    # print results
    print(f"positive_stars: {positive_stars}")
    print(f"negative_stars: {negative_stars}")
    if   positive_stars == 0 and negative_stars == 0:
        #print(f"No trust in need, small price indeed.")
        #print(f"No need for trust in here, just avoid big amounts.")
        print(f"We can be heroes.")
    elif positive_stars >  0 and negative_stars == 0:
        print(f"I've seen better.")
    elif positive_stars == 0 and negative_stars >  0:
        print(f"What can I say.")
    elif positive_stars == negative_stars:
        #print(f"50/50, to do, or not to do.")
        print(f"Welcome to the jungle.")
    else:
        print("%.2f%% of a character, it seems." % (100 * negative_stars / (negative_stars + positive_stars)))


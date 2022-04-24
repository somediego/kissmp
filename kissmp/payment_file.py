import json
import os  # os.path.isfile()

from datetime import datetime

from chia.types.spend_bundle import Coin
from chia.wallet.puzzles.p2_delegated_puzzle_or_hidden_puzzle import puzzle_for_synthetic_public_key




def get_payment_data(payment_file: str, verbosity: bool= False):
    #get dict
    d = {}
    with open(payment_file, "r") as file:
        for line in file:
            (key, val) = line.split(': ')
            if 'cash out' in str(key):
                break
            if 'Version' in str(key):
                key = 'version'
            elif 'Coin ID' in str(key):
                key = 'name'
            elif 'Coin PH' in str(key):
                key = 'ph'
            elif 'Parent' in str(key):
                key = 'parent'
            elif 'Price' in str(key):
                key = 'price_kmojos'
            elif 'Buyer' in str(key):
                key = 'buyer_cupkey'
            elif 'Seller' in str(key):
                key = 'seller_cupkey'
            else:
                continue
            d[str(key)] = str(val)[:-1]
            if 'XCH' in str(val):
                d[str(key)] = int(float(val[:-4]) * 1000000000)
    if verbosity:
        print(f"file_data: {json.dumps(d, indent=4)}")
    return d

def get_payment_file_name(coin_name: str, price: float) -> str:
    return '0x' + str(coin_name)[:3] + str('_%.3fxch'[:10] % price).replace(".", "_") + '.payment'


def create_payment_file(
    file_name: str,
    version,
    payment_coin: Coin,
    amount: dict,
    buyer_cupkey,
    seller_cupkey,
):
    print(f"file_name: {file_name}")
    # create payment file.
    x = datetime.now()
    if os.path.isfile(file_name):
        raise Exception("File {0} already exist, change existing file name if you want to create another.".format(file_name))
    f = open(file_name, 'w')
    f.write('Version: {0}\n'.format(version))
    f.write('Payment Coin ID    : 0x{0}\n'.format(payment_coin.name()))
    f.write('Payment Coin PH    : 0x{0}\n'.format(payment_coin.puzzle_hash))
    f.write('Payment Coin Parent: 0x{0}\n'.format(payment_coin.parent_coin_info))
    f.write("Price: %.9f XCH\n" % (amount['price_kmojos']/1000000000))
    f.write('Buyer\'s  cupkey: 0x{0}\n'.format(buyer_cupkey))
    f.write('Seller\'s cupkey: 0x{0}\n'.format(seller_cupkey))
    f.write('Buyer\'s  cash out ph: 0x{0}\n'.format(puzzle_for_synthetic_public_key(buyer_cupkey).get_tree_hash()))
    f.write('Seller\'s cash out ph: 0x{0}\n'.format(puzzle_for_synthetic_public_key(seller_cupkey).get_tree_hash()))
    f.write("Buyer's  amount to lock   : %.12f XCH\n" % (float(amount['buyer_amount']) / 1000000000000))
    f.write("Seller's amount to deposit: %.12f XCH\n" % (float(amount['seller_amount']) / 1000000000000))
    f.write('Date: ' + x.strftime('%y-%m-%d' + '\n'))
    f.write('##############################################################\nYour Notes:\n-Write in this section whatever you want.\n')
    f.close()

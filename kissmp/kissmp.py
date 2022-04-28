import click
import json
import os  # os.path.isfile()
import pkg_resources  # part of setuptools # version = pkg_resources.require("MyProject")[0].version

from typing import Tuple, List, Any
from blspy import G1Element
from chia.util.byte_types import hexstr_to_bytes
from chia.types.spend_bundle import SpendBundle, CoinSpend, Coin
from chia.wallet.secret_key_store import SecretKeyStore

################
# local
################
from kissmp.keys_management import get_and_save_wallet_keys
from kissmp.bundles import (
    get_buyer_kmp_spendbundle,
    get_seller_kmp_spendbundle,
    fund_kmp_spendbundle,
    contribution_spendbundle_for_seller_to_lock,
    attach_fee_spendbundle,
    contribution_spendbundle_for_reviews,
    create_review_spendbundle,
)
from kissmp.payment_file import get_payment_data, get_payment_file_name, create_payment_file
from kissmp.amounts import (
    DEFAULT_FEE,
    amounts_buyer_create,
    amounts_seller_confirm,
    amounts_buyer_finish,
    amounts_buyer_cancel,
    amounts_seller_cancel,
    amounts_submit_review,
)
from kissmp.final_step import (
    final_step_buyer_create,
    final_step_seller_confirm,
    final_step_buyer_cancel,
    final_step_seller_cancel,
    final_step_buyer_finish,
    final_step_submit_review,
)
from kissmp.info_request import show_payment_info, show_review_info
from kissmp.kissmp_drivers import (
    create_review_puzzle,
)



@click.command("create", short_help="Create payment_file.")
@click.option("--seller_cupkey",required=True,prompt="seller's CupKey",help="seller's CupKey.",)
@click.option("-p","--price",required=True,type=float,prompt="price in XCH",help="price in XCH",)
@click.option("-m","--fee",required=False,default=DEFAULT_FEE,show_default=True,help="mojo fee to use for this issuance",)
@click.option("-v","--verbosity",is_flag=True,help="Show extra info.",)
def buyer_create(
    seller_cupkey: str,
    price: float,
    fee: int,
    verbosity: bool,
):
    # amounts
    amount=  amounts_buyer_create(price, fee, verbosity)
    # get keys
    secret_key_store: SecretKeyStore = SecretKeyStore()
    pk1, cupkey1 = get_and_save_wallet_keys(secret_key_store, None, verbosity)
    seller_cupkey= G1Element.from_bytes(hexstr_to_bytes(seller_cupkey))
    if verbosity:
        print(f"buyer's  cupkey: 0x{cupkey1}")
        print(f"seller's cupkey: 0x{seller_cupkey}")
    # spend_bundle, and future coin
    final_bundle, kmp_coin= fund_kmp_spendbundle(
        pk1.get_fingerprint(),
        amount,
        cupkey1,
        seller_cupkey,
    )
    # create payment file.
    file_name= get_payment_file_name(str(kmp_coin.name()), amount['price'])
    create_payment_file(
        file_name,
        pkg_resources.require("kissmp")[0].version,
        kmp_coin,
        amount,
        cupkey1,
        seller_cupkey,
    )
    # final step
    confirmation= final_step_buyer_create(
        pk1.get_fingerprint(),
        amount,
        final_bundle,
        kmp_coin,
        file_name,
        verbosity,
    )
    if confirmation == False:
        os.remove(file_name)



@click.command("confirm", short_help="Confirm sell.")
@click.argument('payment_file')
@click.option("-m","--fee",required=False,default=DEFAULT_FEE,show_default=True,help="mojo fee to use for this issuance",)
@click.option("-v","--verbosity",is_flag=True,help="Show extra info.",)
def seller_confirm(
    fee: int,
    verbosity: bool,
    payment_file: str,
):
    # file data, dict
    file = get_payment_data(payment_file, verbosity)
    # amounts to lock payment
    amount=  amounts_seller_confirm(file, fee, verbosity)
    # get keys
    secret_key_store: SecretKeyStore = SecretKeyStore()
    pk1, cupkey1 = get_and_save_wallet_keys(secret_key_store, file['seller_cupkey'], verbosity)
    # kmp bundle
    kmp_spendbundle= get_seller_kmp_spendbundle(
        file,
        amount,
        cupkey1,
        file['parent'],
        secret_key_store,
        verbosity,
    )
    # contribution bundle
    contribution_spendbundle= contribution_spendbundle_for_seller_to_lock(
        file,
        amount,
        pk1,
        kmp_spendbundle.coin_spends[0],
        secret_key_store,
        verbosity,
    )
    # Aggregate everything together
    final_bundle = SpendBundle.aggregate([kmp_spendbundle, contribution_spendbundle])
    # final step
    final_step_seller_confirm(
        pk1.get_fingerprint(),
        file,
        amount,
        final_bundle,
        kmp_spendbundle.coin_spends[0].coin,
        verbosity,
    )


@click.command("finish", short_help="Finish trade, a happy ending.")
@click.argument('payment_file')
@click.option("-m","--fee",required=False,default=DEFAULT_FEE,show_default=True,help="mojo fee to use for this issuance",)
@click.option("-v","--verbosity",is_flag=True,help="Show extra info.",)
def buyer_finish(
    fee: int,
    verbosity: bool,
    payment_file: str,
):
    # file data, dict
    file = get_payment_data(payment_file, verbosity)
    # amounts to finish trade
    amount=  amounts_buyer_finish(file, fee, verbosity)
    # get keys
    secret_key_store: SecretKeyStore = SecretKeyStore()
    pk1, cupkey1 = get_and_save_wallet_keys(secret_key_store, file['buyer_cupkey'], verbosity)
    # kmp bundle
    kmp_spendbundle= get_buyer_kmp_spendbundle(
        file,
        amount,
        cupkey1,
        file['name'],
        secret_key_store,
        verbosity,
    )
    # attach extra transaction with network fee to push if forward
    if amount['fee'] > 0:
        attached_spendbundle= attach_fee_spendbundle(
            pk1.get_fingerprint(),
            amount,
            kmp_spendbundle.coin_spends[0].coin,
        )
        # Aggregate everything together
        final_bundle = SpendBundle.aggregate([attached_spendbundle, kmp_spendbundle])
    else:
        final_bundle = kmp_spendbundle
    # final step
    final_step_buyer_finish(
        pk1.get_fingerprint(),
        file,
        amount,
        final_bundle,
        kmp_spendbundle.coin_spends[0].coin,
        verbosity,
    )


@click.command("cancel", short_help="Cancel payment_file.")
@click.argument('payment_file')
@click.option("-m","--fee",required=False,default=DEFAULT_FEE,show_default=True,help="mojo fee to use for this issuance",)
@click.option("-v","--verbosity",is_flag=True,help="Show extra info.",)
def buyer_cancel(
    fee: int,
    verbosity: bool,
    payment_file: str,
):
    # file data, dict
    file = get_payment_data(payment_file, verbosity)
    # amounts to cancel payment
    amount=  amounts_buyer_cancel(file, fee, verbosity)
    # get keys
    secret_key_store: SecretKeyStore = SecretKeyStore()
    pk1, cupkey1 = get_and_save_wallet_keys(secret_key_store, file['buyer_cupkey'], verbosity)
    # kmp bundle
    kmp_spendbundle= get_buyer_kmp_spendbundle(
        file,
        amount,
        cupkey1,
        file['parent'],
        secret_key_store,
        verbosity,
    )
    # attach extra transaction with network fee to push if forward
    if amount['fee'] > 0:
        attached_spendbundle= attach_fee_spendbundle(
            pk1.get_fingerprint(),
            amount,
            kmp_spendbundle.coin_spends[0].coin,
        )
        # Aggregate everything together
        final_bundle = SpendBundle.aggregate([attached_spendbundle, kmp_spendbundle])
    else:
        final_bundle = kmp_spendbundle
    # final step
    final_step_buyer_cancel(
        pk1.get_fingerprint(),
        file,
        amount,
        final_bundle,
        kmp_spendbundle.coin_spends[0].coin,
        verbosity,
    )

@click.command("cancel", short_help="Cancel sell.")
@click.argument('payment_file')
@click.option("-m","--fee",required=False,default=DEFAULT_FEE,show_default=True,help="mojo fee to use for this issuance",)
@click.option("-v","--verbosity",is_flag=True,help="Show extra info.",)
def seller_cancel(
    fee: int,
    verbosity: bool,
    payment_file: str,
):
    # file data, dict
    file = get_payment_data(payment_file, verbosity)
    # amounts to cancel sell
    amount=  amounts_seller_cancel(file, fee, verbosity)
    # get keys
    secret_key_store: SecretKeyStore = SecretKeyStore()
    pk1, cupkey1 = get_and_save_wallet_keys(secret_key_store, file['seller_cupkey'], verbosity)
    # kmp bundle
    kmp_spendbundle= get_seller_kmp_spendbundle(
        file,
        amount,
        cupkey1,
        file['name'],
        secret_key_store,
        verbosity,
    )
    # attach extra transaction with network fee to push if forward
    if amount['fee'] > 0:
        attached_spendbundle= attach_fee_spendbundle(
            pk1.get_fingerprint(),
            amount,
            kmp_spendbundle.coin_spends[0].coin,
        )
        # Aggregate everything together
        final_bundle = SpendBundle.aggregate([attached_spendbundle, kmp_spendbundle])
    else:
        final_bundle = kmp_spendbundle
    # final step
    final_step_seller_cancel(
        pk1.get_fingerprint(),
        file,
        amount,
        final_bundle,
        kmp_spendbundle.coin_spends[0].coin,
        verbosity,
    )


@click.command("cupkey", short_help="Your seller CupKey.")
@click.option("-v","--verbosity",is_flag=True,help="Show extra info.",)
def seller_cupkey(
    verbosity: bool,
):
    # get the public key to use as seller ID
    secret_key_store: SecretKeyStore = SecretKeyStore()
    pk1, cupkey1 = get_and_save_wallet_keys(secret_key_store, None, verbosity)
    print(f"Your CupKey: 0x{cupkey1}")
    return


@click.command("info", short_help="Payment stage.")
@click.argument('payment_file')
@click.option("-v","--verbosity",is_flag=True,help="Show extra info.",)
def buyer_info(
    verbosity: bool,
    payment_file: str,
):
    # file data, dict
    file = get_payment_data(payment_file, verbosity)
    # show info
    show_payment_info(file, verbosity)
    return


@click.command("info", short_help="Payment stage.")
@click.argument('payment_file')
@click.option("-v","--verbosity",is_flag=True,help="Show extra info.",)
def seller_info(
    verbosity: bool,
    payment_file: str,
):
    # file data, dict
    file = get_payment_data(payment_file, verbosity)
    # show info
    show_payment_info(file, verbosity)
    return



def submit_review(
    positive: bool,
    fucker_cupkey: str,
    fee: int,
    verbosity: bool,
):
    # amounts
    amount=  amounts_submit_review(fee, verbosity)
    # get keys
    secret_key_store: SecretKeyStore = SecretKeyStore()
    pk1, cupkey1 = get_and_save_wallet_keys(secret_key_store, None, verbosity)
    # Get puzzle
    review_puzzle = create_review_puzzle(
        positive,			# positive/negative review
        hexstr_to_bytes(fucker_cupkey),	# fucker's synthetic wallet public key to use
    )
    # contribution spendbundle
    contribution_spendbundle= contribution_spendbundle_for_reviews(
        pk1.get_fingerprint(),
        amount,
        review_puzzle.get_tree_hash(),
    )
    # future review coin spendbundle
    review_spendbundle= create_review_spendbundle(
        amount,
        review_puzzle,
        contribution_spendbundle,
        secret_key_store,
    )
    # Aggregate everything together
    final_bundle = SpendBundle.aggregate([contribution_spendbundle, review_spendbundle])
    # final step
    final_step_submit_review(
        pk1.get_fingerprint(),
        amount,
        final_bundle,
        review_spendbundle.coin_spends[0].coin,
        verbosity,
    )


@click.command("negative", short_help="Give a negative star to someone's cupkey, plus mantain this twat project.")
@click.option("--fuck_cupkey",required=True,prompt="Someone\'s cupkey that pissed you off",help="Someone\'s cupkey that pissed you off.",)
@click.option("-m","--fee",required=False,default=DEFAULT_FEE,show_default=True,help="mojo fee to use for this issuance",)
@click.option("-v","--verbosity",is_flag=True,help="Show extra info.",)
def review_negative(
    fuck_cupkey: str,
    fee: int,
    verbosity: bool,
):
    positive: bool= 0	# zero for negative review
    submit_review(positive, fuck_cupkey, fee, verbosity)
    return

@click.command("positive", short_help="Give a positive star to someone's cupkey, plus mantain this twat project.")
@click.option("--nice_cupkey",required=True,prompt="Someone\'s cupkey to give a positive review",help="Someone\'s cupkey to give a positive review.",)
@click.option("-m","--fee",required=False,default=DEFAULT_FEE,show_default=True,help="mojo fee to use for this issuance",)
@click.option("-v","--verbosity",is_flag=True,help="Show extra info.",)
def review_positive(
    nice_cupkey: str,
    fee: int,
    verbosity: bool,
):
    positive: bool= 1
    submit_review(positive, nice_cupkey, fee, verbosity)
    return


@click.command("info", short_help="Show some cupkey's info.")
@click.option("--cupkey",required=True,prompt="Cupkey to show",help="Public key to show.",)
@click.option("-v","--verbosity",is_flag=True,help="Show extra info.",)
def review_info(
    cupkey: str,
    verbosity: bool,
):
    show_review_info(cupkey, verbosity)


@click.group(short_help="Buyer options.")
def buyer():
    pass
@click.group(short_help="Seller options.")
def seller():
    pass
@click.group(short_help="Review options.")
def review():
    pass

buyer.add_command(buyer_create)
buyer.add_command(buyer_cancel)
buyer.add_command(buyer_finish)
buyer.add_command(buyer_info)
seller.add_command(seller_confirm)
seller.add_command(seller_cancel)
seller.add_command(seller_cupkey)
seller.add_command(seller_info)
review.add_command(review_negative)
review.add_command(review_positive)
review.add_command(review_info)
@click.group(context_settings={'help_option_names':['-h','--help']})
@click.version_option(pkg_resources.require("kissmp")[0].version)
def order():
    pass

order.add_command(buyer)
order.add_command(seller)
order.add_command(review)
def cli():
    order()

def main():
    cli()

if __name__ == "__main__":
    main()

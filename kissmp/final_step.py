import asyncio

from clvm.casts import int_to_bytes
from chia.util.hash import std_hash
from chia.util.byte_types import hexstr_to_bytes
from chia.types.spend_bundle import SpendBundle, CoinSpend, Coin

from chia.wallet.puzzles.p2_delegated_puzzle_or_hidden_puzzle import (
    puzzle_for_synthetic_public_key,
)
from kissmp.wallet_rpc import push_tx, get_network
from kissmp.amounts import DEFAULT_FEE, TRILLION


def print_final_bundle(final_bundle: SpendBundle, fee, verbosity:bool= False):
    final_bundle_dump = bytes(final_bundle).hex()
    #final_bundle_dump = json.dumps(final_bundle.to_json_dict(), sort_keys=True, indent=4)
    if verbosity:
        print(f"\n##########\nSpend Bundle: {final_bundle_dump}\n##########\n")
    if fee == DEFAULT_FEE:
        print(f"\nnetwork fee to use: {fee} mojos,             use '--fee <amount>' command to change it.")
    else:
        print(f"\nnetwork fee to use: {fee} mojos")


def get_confirmation(final_bundle: SpendBundle, fingerprint: int, verbosity:bool= False) -> bool:
    confirmation = input(
        "The transaction has been created, would you like to push it to the network? (Y/N)"
    ) in ["y", "Y", "yes", "Yes"]
    if confirmation:
        response = asyncio.get_event_loop().run_until_complete(
            push_tx(fingerprint, final_bundle)
        )
        if "error" in response:
            print(f"Error pushing transaction: {response['error']}")
            return None
        if response['success'] == False:
            print(f"response : {response}")
            return None
    return confirmation


def check_this_is_mainnet():
    present_network= get_network()
    if "mainnet" != present_network:
        print(f"IF YOU WERE ON MAINNET, THAT YOU ARE NOT!!.->{present_network}")
    return

def message_on_confirm(coin_name):
    print(f"Sending to network, in progress.")
    print(f"Transaction shoud appear at https://chia.tt/info/coin/0x{coin_name}")
    check_this_is_mainnet()


def final_step_buyer_create(
    fingerprint: int,
    amount: dict,
    final_bundle: SpendBundle,
    payment_coin: Coin,
    file_name: str,
    verbosity: bool,
)-> bool:
    print_final_bundle(final_bundle, amount['fee'], verbosity)
    print(f"seller's amount he will need to lock payment: %.12f XCH" % (float(amount['seller_amount']) / TRILLION))
    print(f"Our yet unlocked payment amount and deposit : %.12f XCH" % (float(amount['buyer_amount']) / TRILLION))
    confirmation= get_confirmation(final_bundle, fingerprint, verbosity)
    future_coin_name= payment_coin.name()
    if verbosity:
        print(f"Asset ph: 0x{payment_coin.puzzle_hash}")
        print(f"Asset ID: 0x{future_coin_name}")
    if confirmation:
        message_on_confirm(future_coin_name)
        print(f"Payment file: {file_name}")
        print(f"Send a copy to the seller, if transaction goes through.")
    else:
        print(f"Cancelled.")
    return confirmation

def final_step_seller_confirm(
        fingerprint: int,
        file: dict,
        amount: dict,
        final_bundle: SpendBundle,
        payment_coin: Coin,
        verbosity: bool,
    ):
    print_final_bundle(final_bundle, amount['fee'], verbosity)
    print(f"price                     : %.12f XCH" % (float(file['price_kmojos']*1000) / TRILLION))
    print(f"buyer's  amount to lock   : %.12f XCH" % (float(amount['old']) / TRILLION))
    print(f"seller's amount to deposit: %.12f XCH" % (float(amount['deposit'] + amount['penalty']) / TRILLION))
    confirmation= get_confirmation(final_bundle, fingerprint, verbosity)
    future_coin_name= std_hash(payment_coin.name() + payment_coin.puzzle_hash + int_to_bytes(amount['new']))
    if verbosity:
        print(f"Asset puzzle_hash : 0x{payment_coin.puzzle_hash}")
        print(f"Asset ID to spend : 0x{payment_coin.name()}")
        print(f"Asset ID to create: 0x{future_coin_name}")
    if confirmation:
        message_on_confirm(future_coin_name)
        print(f"Start trade, if transaction goes through.")
    else:
        print(f"Cancelled.")

def final_step_buyer_cancel(
        fingerprint: int,
        file: dict,
        amount: dict,
        final_bundle: SpendBundle,
        payment_coin: Coin,
        verbosity: bool,
    ):
    print_final_bundle(final_bundle, amount['fee'], verbosity)
    print(f"Get back our payment and deposit amount: %.12f XCH" % (float(amount['old']) / TRILLION))
    confirmation= get_confirmation(final_bundle, fingerprint, verbosity)
    future_coin_name= std_hash(payment_coin.name() + puzzle_for_synthetic_public_key(hexstr_to_bytes(file['buyer_cupkey'])).get_tree_hash() + int_to_bytes(amount['old']))
    if verbosity:
        print(f"Asset puzzlehash   : 0x{payment_coin.puzzle_hash}")
        print(f"Asset ID to spend  : 0x{payment_coin.name()}")
        print(f"Cash out puzzlehash: 0x{puzzle_for_synthetic_public_key(hexstr_to_bytes(file['buyer_cupkey'])).get_tree_hash()}")
        print(f"Cash out ID        : 0x{future_coin_name}")
    if confirmation:
        message_on_confirm(future_coin_name)
        print(f"and all the amount in your wallet, if seller has not locked that yet.")
    else:
        print(f"Cancelled.")


def final_step_seller_cancel(
        fingerprint: int,
        file: dict,
        amount: dict,
        final_bundle: SpendBundle,
        payment_coin: Coin,
        verbosity: bool,
    ):
    confirmation = input("Did you deliver your part of the trade? (Y/N)") in ["y", "Y", "yes", "Yes"]
    if confirmation:
        print(f"Then you must wait for buyer to confirm. And %.12f XCH will appear in your wallet." % (float(amount['old'] - amount['deposit'])/ TRILLION))
        return
    print(f"\nAs seller, you will pay a penalty to buyer of %.12f XCH for locking his money without delivering." % (float(amount['penalty'])/ TRILLION))
    print_final_bundle(final_bundle, amount['fee'], verbosity)
    print(f"buyer's  amount to unlock: %.12f XCH" % (float(amount['old'] - amount['deposit']) / TRILLION))
    print(f"Get back our deposit amount: %.12f XCH" % (float(amount['deposit']) / TRILLION))
    confirmation= get_confirmation(final_bundle, fingerprint, verbosity)
    future_coin_name= std_hash(payment_coin.name() + puzzle_for_synthetic_public_key(hexstr_to_bytes(file['seller_cupkey'])).get_tree_hash() + int_to_bytes(amount['deposit']))
    if verbosity:
        print(f"Asset puzzlehash   : 0x{payment_coin.puzzle_hash}")
        print(f"Asset ID to spend  : 0x{payment_coin.name()}")
        print(f"Cash out puzzlehash: 0x{puzzle_for_synthetic_public_key(hexstr_to_bytes(file['seller_cupkey'])).get_tree_hash()}")
        print(f"Cash out ID        : 0x{future_coin_name}")
    if confirmation:
        message_on_confirm(future_coin_name)
        print(f"and deposit amount in your wallet, if it was a locked payment.")
    else:
        print(f"Cancelled.")

def final_step_buyer_finish(
        fingerprint: int,
        file: dict,
        amount: dict,
        final_bundle: SpendBundle,
        payment_coin: Coin,
        verbosity: bool,
    ):
    print_final_bundle(final_bundle, amount['fee'], verbosity)
    print(f"seller's deposit back to him       : %.12f XCH" % (float(amount['seller_deposit']) / TRILLION))
    print(f"payment will be delivered to seller: %.12f XCH" % (float(amount['old'] - amount['buyer_deposit'] - amount['seller_deposit']) / TRILLION))
    print(f"Get back our deposit amount        : %.12f XCH" % (float(amount['buyer_deposit']) / TRILLION))
    confirmation= get_confirmation(final_bundle, fingerprint, verbosity)
    future_coin_name= std_hash(payment_coin.name() + puzzle_for_synthetic_public_key(hexstr_to_bytes(file['buyer_cupkey'])).get_tree_hash() + int_to_bytes(amount['buyer_deposit']))
    if verbosity:
        print(f"Asset puzzlehash   : 0x{payment_coin.puzzle_hash}")
        print(f"Asset ID to spend  : 0x{payment_coin.name()}")
        print(f"Cash out puzzlehash: 0x{puzzle_for_synthetic_public_key(hexstr_to_bytes(file['buyer_cupkey'])).get_tree_hash()}")
        print(f"Cash out ID        : 0x{future_coin_name}")
    if confirmation:
        message_on_confirm(future_coin_name)
        print(f"and deposit amount in your wallet, if it was a locked payment.")
    else:
        print(f"Cancelled.")


def final_step_submit_review(
        fingerprint: int,
        amount: dict,
        final_bundle: SpendBundle,
        review_coin: Coin,
        verbosity: bool,
    ):
    print_final_bundle(final_bundle, amount['fee'], verbosity)
    print(f"twats treasury reserve contribution: %.12f XCH" % (float(amount['treasury']) / TRILLION))
    confirmation= get_confirmation(final_bundle, fingerprint, verbosity)
    future_coin_name= review_coin.name()
    if verbosity:
        print(f"Asset puzzlehash: 0x{review_coin.puzzle_hash}")
        print(f"Asset ID        : 0x{future_coin_name}")
    if confirmation:
        message_on_confirm(future_coin_name)
    else:
        print(f"Cancelled.")

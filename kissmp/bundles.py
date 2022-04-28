import asyncio

from typing import Tuple, List, Any
from blspy import G2Element, AugSchemeMPL, G1Element
from chia.util.byte_types import hexstr_to_bytes
from chia.types.blockchain_format.program import Program
from chia.types.spend_bundle import SpendBundle, CoinSpend, Coin
from chia.util.hash import std_hash
from clvm.casts import int_to_bytes

from chia.wallet.puzzles.p2_delegated_puzzle_or_hidden_puzzle import (
    puzzle_for_synthetic_public_key,
)
from chia.wallet.sign_coin_spends import sign_coin_spends
from chia.types.announcement import Announcement
from chia.types.condition_opcodes import ConditionOpcode

from kissmp.wallet_rpc import get_signed_tx, get_genesis, get_wallets, get_next_puzzle_hash
from kissmp.keys_management import get_and_save_keys_by_puzzle_hash

from kissmp.kissmp_drivers import (
    create_kissmp_puzzle,
    solution_for_kissmp,
    kissmp_announcement_assertion,

    create_review_puzzle,
    solution_for_review,
)



MAX_BLOCK_COST_CLVM= 11000000000

def get_wallet_id(fingerprint, verbosity:bool= False)-> int:
    data= get_wallets(fingerprint)
    wallet_id:int = 1
    for i in range(len(data)):
        if data[i]['type']== 0 and data[i]['name']== "Chia Wallet":
            wallet_id=data[i]['id']
            break
    if verbosity:
        print(f"wallet_id: {wallet_id}")
    return wallet_id


#attach extra transaction with network fee to push smart coin spendbundle forward
def attach_fee_spendbundle(
    fingerprint: int,
    amount: dict,
    attached_coin: Coin,
) -> SpendBundle:
        tx_coin_announcements = [Announcement(
            attached_coin.name(),  # coin id
            std_hash(int_to_bytes(amount['new'])),  # message
        ),]
        # fee spend
        amount_to_move= 0
        signed_tx = asyncio.get_event_loop().run_until_complete(
            get_signed_tx(fingerprint, attached_coin.puzzle_hash, amount_to_move, amount['fee'], tx_coin_announcements)
        )
        #print(f"\n##########\nsigned_tx: {signed_tx}\n##########\n")
        return signed_tx.spend_bundle


def get_kmp_coinspend(
    file: dict,
    amount: dict,
    buyer_synth_wallet_pk: G1Element,
    seller_synth_wallet_pk: G1Element,
    user_synth_wallet_pk: G1Element,
    parent: str,
    verbosity: bool= False
) -> CoinSpend:
    # kmp spend
    kmp_puzzle = create_kissmp_puzzle(
        buyer_synth_wallet_pk,
        seller_synth_wallet_pk,
        puzzle_for_synthetic_public_key(buyer_synth_wallet_pk).get_tree_hash(),  # buyer_ph,
        puzzle_for_synthetic_public_key(seller_synth_wallet_pk).get_tree_hash(),  # seller_ph
        file['price_kmojos'],
    )
    kmp_coin: Coin = Coin(hexstr_to_bytes(parent), kmp_puzzle.get_tree_hash(), amount['old'])
    kmp_solution = solution_for_kissmp(user_synth_wallet_pk, kmp_coin, amount['new'])
    kmp_spend = CoinSpend(
        coin=kmp_coin, puzzle_reveal=kmp_puzzle, solution=kmp_solution
    )
    # check posted ph && coin_id info
    assert (
        str(kmp_puzzle.get_tree_hash()) == file['ph'][2:]
    ),"Puzzle_hash to use, do not match \"payment_file\" puzzle_hash.\nph_to_assert: {0} \nph_to_assert: {1}".format(
        kmp_puzzle.get_tree_hash(), file['ph'][2:]
    )
    assert (
        str(Coin(hexstr_to_bytes(file['parent']), kmp_puzzle.get_tree_hash(), (file['price_kmojos']*1250)).name()) == file['name'][2:]
    ),"Coin_id from payment_file do not fit your values.\ncoin_id_to_assert: {0} \ncoin_id_to_assert: {1}".format(
        Coin(hexstr_to_bytes(file['parent']), kmp_puzzle.get_tree_hash(), (file['price_kmojos']*1250)).name(), file['name'][2:]
    )
    return kmp_spend

def get_buyer_kmp_spendbundle(
    file: dict,
    amount: dict,
    cupkey1: G1Element,
    parent: str,  # different cases, different file value.
    secret_key_store: Any,
    verbosity: bool,
) -> SpendBundle:
    # seller cupkey
    seller_cupkey= G1Element.from_bytes(hexstr_to_bytes(file['seller_cupkey']))
    # kmp spend
    kmp_coinspend= get_kmp_coinspend(file, amount, cupkey1, seller_cupkey, cupkey1, parent, verbosity)
    # signatures and spend_bundle
    kmp_spendbundle = asyncio.get_event_loop().run_until_complete(
        sign_coin_spends(
          [kmp_coinspend],
          secret_key_store.secret_key_for_public_key,
          get_genesis(),
          MAX_BLOCK_COST_CLVM,
        )
    )
    return kmp_spendbundle

def get_seller_kmp_spendbundle(
    file: dict,
    amount: dict,
    cupkey1: G1Element,
    parent: str,  # different cases, different file value.
    secret_key_store: Any,
    verbosity: bool,
) -> SpendBundle:
    # buyer cupkey
    buyer_cupkey= G1Element.from_bytes(hexstr_to_bytes(file['buyer_cupkey']))
    # kmp spend
    kmp_coinspend= get_kmp_coinspend(file, amount, buyer_cupkey, cupkey1, cupkey1, parent, verbosity)
    # signatures and spend_bundle
    kmp_spendbundle = asyncio.get_event_loop().run_until_complete(
        sign_coin_spends(
          [kmp_coinspend],
          secret_key_store.secret_key_for_public_key,
          get_genesis(),
          MAX_BLOCK_COST_CLVM,
        )
    )
    return kmp_spendbundle


def fund_kmp_spendbundle(
    fingerprint: int,
    amount: dict,
    buyer_synth_wallet_pk: G1Element,
    seller_synth_wallet_pk: G1Element,
) -> List:
    # Get puzzle
    kmp_puzzle = create_kissmp_puzzle(
        buyer_synth_wallet_pk,	# buyer's  synthetic wallet public key to use
        seller_synth_wallet_pk,	# seller's synthetic wallet public key to use
        puzzle_for_synthetic_public_key(buyer_synth_wallet_pk).get_tree_hash(),    # buyer's  cashout puzzlehash
        puzzle_for_synthetic_public_key(seller_synth_wallet_pk).get_tree_hash(),   # seller's cashout puzzlehash
        amount['price_kmojos'],
    )
    # signed_tx
    signed_tx = asyncio.get_event_loop().run_until_complete(
        get_signed_tx(fingerprint, kmp_puzzle.get_tree_hash(), amount['buyer_amount'], amount['fee'])
    )
    # future payment coin
    kmp_coin: Coin = list(
        filter(lambda c: c.puzzle_hash == kmp_puzzle.get_tree_hash(), signed_tx.spend_bundle.additions())
    )[0]
    # return bundle plus coin
    return [signed_tx.spend_bundle, kmp_coin]

def contribution_spendbundle_for_seller_to_lock(
    file: dict,
    amount: dict,
    pk1: G1Element,
    kmp_coinspend: CoinSpend,
    secret_key_store: Any,
    verbosity: bool,
) -> SpendBundle:
    # select coins
    signed_tx = asyncio.get_event_loop().run_until_complete(
        get_signed_tx(pk1.get_fingerprint(), kmp_coinspend.coin.puzzle_hash, amount['contribution'], amount['fee'])
    )
    number_of_selected_coins= len(signed_tx.spend_bundle.coin_spends)
    if verbosity:
        print(f"number_of_selected_coins == {number_of_selected_coins}")
        #print(f"\n##########\nsigned_tx: {signed_tx}\n##########\n")

    if number_of_selected_coins > 1:
        #############################################################
        # if more than one selected coin, combine coins into one single coin.
        #############################################################
        if len(signed_tx.spend_bundle.additions()) > 1:
            amount_left = list(filter(lambda c: c.puzzle_hash != kmp_coinspend.coin.puzzle_hash, signed_tx.spend_bundle.additions()))[0].amount
            some_new_amount= amount['contribution'] + amount['fee'] + amount_left
        else:
            some_new_amount= amount['contribution'] + amount['fee']
        # Add custom assert coin announcement
        tx_coin_announcements = [ Announcement(
            kmp_coinspend.coin.name(),  # coin id
            std_hash(int_to_bytes(amount['new'])),  # message
        ),]
        some_puzzle_hash= get_next_puzzle_hash(pk1.get_fingerprint(), get_wallet_id(pk1.get_fingerprint()))
        some_fee= 0
        combined_signed_tx = asyncio.get_event_loop().run_until_complete(
            get_signed_tx(pk1.get_fingerprint(), some_puzzle_hash, some_new_amount, some_fee, tx_coin_announcements)
        )
        #if verbosity:
        #    print(f"\n##########\ncombined_signed_tx: {combined_signed_tx}\n##########\n")

        #############################################################
        # create contribution CoinSpend
        #############################################################
        if len(combined_signed_tx.spend_bundle.additions()) > 1:
            raise Exception("Some undetermined/unclear error here. Additions == {0}, should be 2.".format(len(combined_signed_tx.spend_bundle.additions())))

        contribution_coin: Coin = combined_signed_tx.spend_bundle.additions()[0]
        synth_wallet_pk2 = get_and_save_keys_by_puzzle_hash(secret_key_store, pk1, contribution_coin.puzzle_hash, verbosity)
        contribution_puzzle: Program = puzzle_for_synthetic_public_key(synth_wallet_pk2)
        amount_back_to_wallet= contribution_coin.amount - amount['contribution'] - amount['fee']
        solution_list: List[List] = [
                [ConditionOpcode.CREATE_COIN, contribution_coin.puzzle_hash, amount_back_to_wallet],
                [ConditionOpcode.RESERVE_FEE, amount['fee']],
                kissmp_announcement_assertion(kmp_coinspend.coin, amount['contribution'])
            ]
        delegated_puzzle_solution = Program.to((1, solution_list))
        contribution_solution = Program.to([[], delegated_puzzle_solution, []])
        contribution_spend = CoinSpend(
            coin=contribution_coin, puzzle_reveal=contribution_puzzle, solution=contribution_solution
        )
        assert (
            contribution_coin.puzzle_hash == contribution_puzzle.get_tree_hash()
        ),"coin_ph, should be equal to puzzle_reveal_ph.\ncoin_ph     : {0} \nph_to_assert: {1}".format(
            contribution_coin.puzzle_hash, contribution_puzzle.get_tree_hash()
        )
    else:
        #############################################################
        # if one selected coin. create contribution CoinSpend
        #############################################################
        additions_coin = list(
            filter(lambda c: c.puzzle_hash != kmp_coinspend.coin.puzzle_hash, signed_tx.spend_bundle.additions())
        )[0]
        contribution_puzzle: Program = signed_tx.spend_bundle.coin_spends[0].puzzle_reveal
        contribution_coin: Coin = signed_tx.spend_bundle.coin_spends[0].coin
        solution_list: List[List] = [
                [ConditionOpcode.CREATE_COIN, additions_coin.puzzle_hash, additions_coin.amount],
                [ConditionOpcode.RESERVE_FEE, amount['fee']],
                kissmp_announcement_assertion(kmp_coinspend.coin, amount['contribution'])
            ]
        delegated_puzzle_solution = Program.to((1, solution_list))
        contribution_solution = Program.to([[], delegated_puzzle_solution, []])
        contribution_spend = CoinSpend(
            coin=contribution_coin, puzzle_reveal=contribution_puzzle, solution=contribution_solution
        )
        if verbosity:
            #print(f"\n##########\nsigned_tx: {signed_tx}\n##########\n")
            #print(f"signed_tx_ph: {signed_tx.spend_bundle.coin_spends[0].coin.puzzle_hash}")
            print(f"additions_coin.amount: {additions_coin.amount}")
            #print(f"delegated_puzzle_solution: {delegated_puzzle_solution}")

        # get contribution coin keys
        synth_wallet_pk2 = get_and_save_keys_by_puzzle_hash(secret_key_store, pk1, contribution_puzzle.get_tree_hash(), verbosity)

    #############################################################
    # signatures and spend_bundle
    #############################################################
    contribution_spendbundle = asyncio.get_event_loop().run_until_complete(
        sign_coin_spends(
          [contribution_spend],
          secret_key_store.secret_key_for_public_key,
          get_genesis(),
          MAX_BLOCK_COST_CLVM,
        )
    )
    # Aggregate everything together
    if number_of_selected_coins > 1:
        spend_bundle = SpendBundle.aggregate([combined_signed_tx.spend_bundle, contribution_spendbundle])
    else:
        spend_bundle = contribution_spendbundle
    return spend_bundle


def contribution_spendbundle_for_reviews(
    fingerprint: int,
    amount: dict,
    review_coin_ph,
) -> SpendBundle:
    # Announcement
    tx_puzzle_announcements = [
        Announcement(
            review_coin_ph,  # coin puzzle
            std_hash(int_to_bytes(amount['treasury'])),  # message
        ),
    ]
    # signed_tx
    signed_tx = asyncio.get_event_loop().run_until_complete(
        get_signed_tx(fingerprint, review_coin_ph, amount['treasury'], amount['fee'], puzzle_ann=tx_puzzle_announcements)
    )
    return signed_tx.spend_bundle


def create_review_spendbundle(
    amount: dict,
    review_puzzle: Program,
    contribution_spendbundle: SpendBundle,
    secret_key_store: Any,
) -> SpendBundle:
    # future review coin
    review_coin: Coin = list(
        filter(lambda c: c.puzzle_hash == review_puzzle.get_tree_hash(), contribution_spendbundle.additions())
    )[0]
    review_solution = solution_for_review(amount['treasury'])
    review_coinspend = CoinSpend(
        coin=review_coin, puzzle_reveal=review_puzzle, solution=review_solution
    )
    # signatures and spend_bundle
    spend_bundle = asyncio.get_event_loop().run_until_complete(
        sign_coin_spends(
          [review_coinspend],
          secret_key_store.secret_key_for_public_key,
          get_genesis(),
          MAX_BLOCK_COST_CLVM,
        )
    )
    return spend_bundle

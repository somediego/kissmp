from chia.types.blockchain_format.coin import Coin
from chia.types.blockchain_format.program import Program
from chia.types.condition_opcodes import ConditionOpcode
from chia.util.hash import std_hash
from clvm.casts import int_to_bytes

from kissmp.wallet_rpc import parse_program


KISSMP_MOD = parse_program(
    "./puzzles/kissmp.clsp.hex",
    ["./include"],
)


# Create a smartcoin
def create_kissmp_puzzle(buyer_pubkey, seller_pubkey, buyer_puzzlehash, seller_puzzlehash, price_kmojos):
    return KISSMP_MOD.curry(buyer_pubkey, seller_pubkey, buyer_puzzlehash, seller_puzzlehash, price_kmojos)

# Generate a solution to contribute to a smartcoin
def solution_for_kissmp(spend_pubkey, pb_coin: Coin, new_amount):
    return Program.to([spend_pubkey, pb_coin.amount, new_amount, pb_coin.puzzle_hash])

# Return the condition to assert the announcement
def kissmp_announcement_assertion(pb_coin: Coin, contribution_amount):
    return [ConditionOpcode.ASSERT_COIN_ANNOUNCEMENT, std_hash(pb_coin.name() + std_hash(int_to_bytes((pb_coin.amount + contribution_amount))))]


REVIEW_MOD = parse_program(
    "./puzzles/review.clsp.hex",
    ["./include"],
)
# Create a snmarcoin
def create_review_puzzle(positive, review_pubkey):
    return REVIEW_MOD.curry(positive, review_pubkey)
# Generate a solution for review_coin
def solution_for_review(my_amount):
    return Program.to([my_amount])

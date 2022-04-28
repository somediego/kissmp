import asyncio

from typing import List, Any
from blspy import G2Element, AugSchemeMPL, PrivateKey, G1Element
from chia.util.byte_types import hexstr_to_bytes
from chia.types.blockchain_format.sized_bytes import bytes32

from chia.wallet.derive_keys import master_sk_to_wallet_sk   #, master_sk_to_wallet_sk_unhardened # unhardened to derivate a key that can be related to other addresses

from chia.wallet.puzzles.p2_delegated_puzzle_or_hidden_puzzle import (
    DEFAULT_HIDDEN_PUZZLE_HASH,
    calculate_synthetic_secret_key,
)

from kissmp.wallet_state_keys import get_keys
from kissmp.wallet_rpc import get_fingerprints, get_private_key




def choose_wallet_fingerprint( verbosity: bool= False) -> int:
    fingerprints= get_fingerprints()
    selection: int = 0
    if len(fingerprints) > 1:
        print(f"Wallet keys:")
        for i in range(len(fingerprints)):
            print(f"{i+1}) {fingerprints[i]}")
        selection = int(input("Enter a number to pick:"))
        if selection < 1 or selection > (len(fingerprints)):
            selection = 1
        selection -= 1
    if verbosity:
        print(f"selected fingerprint: {fingerprints[selection]}")
    return fingerprints[selection]


def get_and_save_wallet_keys(
    secret_key_store_c: Any,  # Potentially awaitable class
    synth_wallet_pk_to_assert_from_payment_file: str = None,   # optional, cupkey from file
    verbosity: bool = False,   # optional
) -> List[G1Element]:
    # some index number to use for no reason
    index_to_use = 84
    # keys
    fingerprint = choose_wallet_fingerprint(verbosity)
    sk1= PrivateKey.from_bytes(hexstr_to_bytes(get_private_key(fingerprint)['sk']))
    wallet_sk1 = master_sk_to_wallet_sk(sk1, index_to_use)  # sk & index
    synth_wallet_sk1 = calculate_synthetic_secret_key(wallet_sk1, DEFAULT_HIDDEN_PUZZLE_HASH)
    # save it
    secret_key_store_c.save_secret_key(sk1)
    secret_key_store_c.save_secret_key(wallet_sk1)
    secret_key_store_c.save_secret_key(synth_wallet_sk1)
    # assert
    if synth_wallet_pk_to_assert_from_payment_file is not None:
        assert (
            str(synth_wallet_sk1.get_g1()) == synth_wallet_pk_to_assert_from_payment_file[2:].zfill(96)
        ),"Your selected public key, do not match cupkey from payment_file.\ncupkey_selected : {0} \ncupkey_to_assert: {1}".format(
            synth_wallet_sk1.get_g1(), synth_wallet_pk_to_assert_from_payment_file[2:].zfill(96)
        )
    # return public keys, [master public key && synthetic wallet public key]
    return [sk1.get_g1(), synth_wallet_sk1.get_g1()]


def get_and_save_keys_by_puzzle_hash(
    secret_key_store_c: Any,  # Potentially awaitable class
    public_key: G1Element,
    puzzle_hash: bytes32,
    verbosity: bool=False,
) -> G1Element:
    maybe = asyncio.get_event_loop().run_until_complete(
        get_keys(secret_key_store_c.secret_key_for_public_key(public_key), puzzle_hash, verbosity)
    )
    # wallet keys for puzzle hash
    wallet_pk_for_ph, wallet_sk_for_ph = maybe
    synth_wallet_sk_for_ph = calculate_synthetic_secret_key(wallet_sk_for_ph, DEFAULT_HIDDEN_PUZZLE_HASH)
    secret_key_store_c.save_secret_key(synth_wallet_sk_for_ph)
    # return synthetic wallet public key
    return synth_wallet_sk_for_ph.get_g1()




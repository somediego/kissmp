import aiosqlite
from pathlib import Path

from typing import Optional, Tuple, Iterable, Union, List, Any
from blspy import G2Element, AugSchemeMPL, PrivateKey, G1Element

from chia.types.blockchain_format.sized_bytes import bytes32
from chia.util.default_root import DEFAULT_ROOT_PATH
from chia.util.config import load_config
from chia.util.db_wrapper import DBWrapper
from chia.wallet.derive_keys import master_sk_to_wallet_sk, master_sk_to_wallet_sk_unhardened
from chia.wallet.wallet_puzzle_store import WalletPuzzleStore


async def get_keys(private_key1: PrivateKey, puzzle_hash: bytes32, verbosity: bool= False) -> Optional[Tuple[G1Element, PrivateKey]]:
    try:
        # get db path
        ## from chia.wallet.wallet_node ##
        config = load_config(DEFAULT_ROOT_PATH, "config.yaml")
        db_path_key_suffix = str(private_key1.get_g1().get_fingerprint())
        db_path_replaced: str = (
            config["wallet"]["database_path"]
            .replace("CHALLENGE", config["wallet"]["selected_network"])
            .replace("KEY", db_path_key_suffix)
            .replace("v1", "v2")
        )
        db_path: Path = DEFAULT_ROOT_PATH / db_path_replaced
        if not db_path.exists():
            print(f"no database path.")

        # get db info
        ## from chia.wallet.wallet_state_manager ##
        db_connection: aiosqlite.Connection = await aiosqlite.connect(db_path)
        db_wrapper: DBWrapper = DBWrapper(db_connection)
        puzzle_store: WalletPuzzleStore = await WalletPuzzleStore.create(db_wrapper)
        if verbosity:
            print(f"db_path: {db_path}")

        # get keys
        ## from chia.wallet.wallet_state_manager ##
        record = await puzzle_store.record_for_puzzle_hash(puzzle_hash)

        if record is None:
            raise ValueError(f"No key for this puzzlehash {puzzle_hash}")
        if record.hardened:
            private = master_sk_to_wallet_sk(private_key1, record.index)
            pubkey = private.get_g1()
            return pubkey, private
        private = master_sk_to_wallet_sk_unhardened(private_key1, record.index)
        pubkey = private.get_g1()

        return pubkey, private
    finally:
        await db_connection.close()


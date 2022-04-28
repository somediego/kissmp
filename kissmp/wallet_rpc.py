import aiohttp
import asyncio
import re

from typing import Optional, Iterable, Union, List

from chia.cmds.wallet_funcs import get_wallet
from chia.rpc.wallet_rpc_client import WalletRpcClient
from chia.util.default_root import DEFAULT_ROOT_PATH
from chia.util.config import load_config
from chia.util.ints import uint16
from chia.util.byte_types import hexstr_to_bytes
from chia.types.blockchain_format.program import Program
from clvm_tools.clvmc import compile_clvm_text
from clvm_tools.binutils import assemble

from chia.util.bech32m import decode_puzzle_hash



# Loading the client requires the standard chia root directory configuration that all of the chia commands rely on
async def get_client() -> Optional[WalletRpcClient]:
    try:
        config = load_config(DEFAULT_ROOT_PATH, "config.yaml")
        self_hostname = config["self_hostname"]
        full_node_rpc_port = config["wallet"]["rpc_port"]
        full_node_client = await WalletRpcClient.create(
            self_hostname, uint16(full_node_rpc_port), DEFAULT_ROOT_PATH, config
        )
        return full_node_client
    except Exception as e:
        if isinstance(e, aiohttp.ClientConnectorError):
            print(
                f"Connection error. Check if full node is running at {full_node_rpc_port}"
            )
        else:
            print(f"Exception from 'harvester' {e}")
        return None


async def get_signed_tx(fingerprint, ph, amt, fee, coin_ann=None, puzzle_ann=None):
    try:
        wallet_client: WalletRpcClient = await get_client()
        wallet_client_f, _ = await get_wallet(wallet_client, fingerprint)
        return await wallet_client_f.create_signed_transaction(
            [{"puzzle_hash": ph, "amount": amt}], fee=fee, coin_announcements=coin_ann, puzzle_announcements=puzzle_ann
        )
    finally:
        wallet_client.close()
        await wallet_client.await_closed()


async def push_tx(fingerprint, bundle):
    try:
        wallet_client: WalletRpcClient = await get_client()
        wallet_client_f, _ = await get_wallet(wallet_client, fingerprint)
        return await wallet_client_f.push_tx(bundle)
    finally:
        wallet_client.close()
        await wallet_client.await_closed()

def get_fingerprints():
    async def query():
        try:
            wallet_client: WalletRpcClient = await get_client()
            return await wallet_client.get_public_keys()
        finally:
            wallet_client.close()
            await wallet_client.await_closed()
    return asyncio.get_event_loop().run_until_complete(query())

def get_private_key(fingerprint):
    async def query(fingerprint):
        try:
            wallet_client: WalletRpcClient = await get_client()
            wallet_client_f, _ = await get_wallet(wallet_client, fingerprint)
            return await wallet_client_f.get_private_key(fingerprint)
        finally:
            wallet_client.close()
            await wallet_client.await_closed()
    return asyncio.get_event_loop().run_until_complete(query(fingerprint))

def get_wallets(fingerprint):
    async def query(fingerprint):
        try:
            wallet_client: WalletRpcClient = await get_client()
            wallet_client_f, _ = await get_wallet(wallet_client, fingerprint)
            return await wallet_client_f.get_wallets()
        finally:
            wallet_client.close()
            await wallet_client.await_closed()
    return asyncio.get_event_loop().run_until_complete(query(fingerprint))

def select_coins(fingerprint, amount, wallet_id):
    async def query(fingerprint, amount, wallet_id):
        try:
            wallet_client: WalletRpcClient = await get_client()
            wallet_client_f, _ = await get_wallet(wallet_client, fingerprint)
            return await wallet_client_f.select_coins(amount=amount, wallet_id=wallet_id)
        finally:
            wallet_client.close()
            await wallet_client.await_closed()
    return asyncio.get_event_loop().run_until_complete(query(fingerprint, amount, wallet_id))

def get_wallet_balance(fingerprint, wallet_id):
    async def query(fingerprint, wallet_id):
        try:
            wallet_client: WalletRpcClient = await get_client()
            wallet_client_f, _ = await get_wallet(wallet_client, fingerprint)
            return await wallet_client_f.get_wallet_balance(wallet_id)
        finally:
            wallet_client.close()
            await wallet_client.await_closed()
    return asyncio.get_event_loop().run_until_complete(query(fingerprint, wallet_id))

def get_next_address(fingerprint, wallet_id, new_address: bool= True):
    async def query():
        try:
            wallet_client: WalletRpcClient = await get_client()
            wallet_client_f, _ = await get_wallet(wallet_client, fingerprint)
            return await wallet_client_f.get_next_address(wallet_id, new_address)
        finally:
            wallet_client.close()
            await wallet_client.await_closed()
    return asyncio.get_event_loop().run_until_complete(query())

def get_next_puzzle_hash(fingerprint, wallet_id, new_address: bool= True):
    return decode_puzzle_hash(get_next_address(fingerprint, wallet_id, new_address))


# The clvm loaders in this library automatically search for includable files in the directory './include'
def append_include(search_paths: Iterable[str]) -> List[str]:
    if search_paths:
        search_list = list(search_paths)
        search_list.append("./include")
        return search_list
    else:
        return ["./include"]


def parse_program(program: Union[str, Program], include: Iterable = []) -> Program:
    if isinstance(program, Program):
        return program
    else:
        if "(" in program:  # If it's raw clvm
            prog = Program.to(assemble(program))
        elif "." not in program:  # If it's a byte string
            prog = Program.from_bytes(hexstr_to_bytes(program))
        else:  # If it's a file
            with open(program, "r") as file:
                filestring: str = file.read()
                if "(" in filestring:  # If it's not compiled
                    # TODO: This should probably be more robust
                    if re.compile(r"\(mod\s").search(filestring):  # If it's Chialisp
                        prog = Program.to(
                            compile_clvm_text(filestring, append_include(include))
                        )
                    else:  # If it's CLVM
                        prog = Program.to(assemble(filestring))
                else:  # If it's serialized CLVM
                    prog = Program.from_bytes(hexstr_to_bytes(filestring))
        return prog

def get_network():
        # get network name
        config = load_config(DEFAULT_ROOT_PATH, "config.yaml")
        return config["wallet"]["selected_network"]

def get_genesis():
        # get genesis_challenge
        config = load_config(DEFAULT_ROOT_PATH, "config.yaml")
        network = config["wallet"]["selected_network"]
        challenge = config["farmer"]["network_overrides"]["constants"][network]["GENESIS_CHALLENGE"]
        return hexstr_to_bytes(challenge)

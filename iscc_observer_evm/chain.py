"""Blockchain client"""
import json
import pathlib
from web3 import Web3
from web3.middleware import geth_poa_middleware
import iscc_observer_evm as evm
from loguru import logger as log

__all__ = ["chain", "ch"]

HERE = pathlib.Path(__file__).parent.absolute()

ch = None


def chain():
    global ch
    if ch is None:
        ch = Chain()
    if not ch.w3.isConnected():
        log.error(f"Connection failed to {evm.config.web3_provider_uri}, reconnecting")
        ch = Chain()
    return ch


class Chain:
    def __init__(self):
        self.w3 = Web3(
            Web3.WebsocketProvider(
                evm.config.web3_provider_uri, websocket_timeout=evm.config.read_timeout
            )
        )
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        self.abi = json.load(open(HERE / "abi.json"))
        self.contract = self.w3.eth.contract(evm.config.hub_contract, abi=self.abi)

    def events(self, from_block: int):
        event_filter = self.contract.events.IsccDeclaration.createFilter(fromBlock=from_block)
        return event_filter.get_all_entries()

    def block(self, height: int):
        return self.w3.eth.getBlock(height)

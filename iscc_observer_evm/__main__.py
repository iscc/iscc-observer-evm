# -*- coding: utf-8 -*-
import json
import pathlib
import sys
import time

import iscc_core as ic
import requests
from loguru import logger as log
from web3 import Web3
from web3.middleware import geth_poa_middleware

import iscc_observer_evm as evm

HERE = pathlib.Path(__file__).parent.absolute()

w3 = Web3(Web3.WebsocketProvider(evm.config.web3_url))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
abi = json.load(open(HERE / "abi.json"))


def register(declaration: dict) -> dict:
    headers = {"Authorization": f"Bearer {evm.config.observer_token}"}
    url = f"{evm.config.registry_url}/register"
    response = requests.post(url, json=declaration, headers=headers, timeout=4)
    if response.status_code == 201:
        return response.json()
    print(response.status_code)
    print(response.content)


def main():
    log.info(f" --> starting evm observer")
    log.info(f"web3:\t\t{evm.config.web3_url}")
    log.info(f"chain:\t\t{ic.ST_ID(evm.config.chain_id).name}")
    log.info(f"contract:\t{evm.config.hub_contract}")
    log.info(f"registry:\t{evm.config.registry_url}")
    log.info(f"updates:\tevery {evm.config.update_interval} seconds")

    while not w3.isConnected():
        log.error(f"connection failed to {evm.config.web3_url}")
        time.sleep(evm.config.update_interval)

    co = w3.eth.contract(evm.config.hub_contract, abi=abi)

    while True:
        time.sleep(evm.config.update_interval)
        # check registry status:

        head = evm.registry().head()
        start_height = head.block_height + 1 if head else 0

        if head is not None:
            chain_block = w3.eth.getBlock(head.block_height)
            if head.block_hash != chain_block.hash.hex():
                log.warning(f"registry out of sync at {head}")

        # TODO rollback registry

        event_filter = co.events.IsccDeclaration.createFilter(fromBlock=start_height)
        for event in event_filter.get_all_entries():
            block = w3.eth.getBlock(event.blockNumber)
            declaration = dict(
                timestamp=block.timestamp,
                chain_id=evm.config.chain_id,
                block_height=block.number,
                block_hash=block.hash.hex(),
                tx_idx=event.transactionIndex,
                tx_hash=event.transactionHash.hex(),
                declarer=event.args.declarer,
                iscc_code=event.args.iscc,
                message=event.args.message,
                meta_url=event.args.url,
                registrar=event.args.registrar,
            )
            resp = register(declaration)
            log.info(f"registered {resp['iscc_id']} with did {resp['did']}")


if __name__ == "__main__":
    main()

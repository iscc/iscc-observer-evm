# -*- coding: utf-8 -*-
import pathlib
import time
import click
import iscc_core as ic
from loguru import logger as log
from sentry_sdk import capture_exception

import iscc_observer_evm as evm
from asyncio.exceptions import TimeoutError

HERE = pathlib.Path(__file__).parent.absolute()


def rollback():
    offset = 1
    head = evm.registry().head(offset=offset)
    while True:
        chain_block = evm.chain().block(head.block_height)
        if head.block_hash != chain_block.hash.hex():
            log.warning(
                f"registry out of sync at height {head.block_height} hash {head.block_hash}"
            )
            offset += 1
            head = evm.registry().head(offset=offset)
        else:
            resp = evm.registry().rollback(head.block_hash)
            if resp:
                log.info(f"rolled back to block {resp.block_hash} at height {resp.block_height}")
            break


def update():
    # check registry status:
    head = evm.registry().head()

    if head is not None:
        chain_block = evm.chain().block(head.block_height)
        if head.block_hash != chain_block.hash.hex():
            log.warning(
                f"registry out of sync at height {head.block_height} hash {head.block_hash}"
            )
            rollback()
        return

    start_height = head.block_height + 1 if head else 0

    for event in evm.chain().events(from_block=start_height):
        block = evm.chain().block(event.blockNumber)
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

        # validate iscc-code
        code_obj = ic.Code(event.args.iscc)
        if code_obj.maintype == ic.MT.ID:
            log.warning(f"skipped registration of {event.args.iscc} with mainttype ISCC-ID")
            continue
        clean = ic.iscc_normalize(event.args.iscc)
        valid = ic.iscc_validate(clean, strict=False)
        if valid is False:
            log.warning(f"skipped registration of invalid ISCC {event.args.iscc}")
            continue

        resp = evm.registry().register(declaration)
        log.info(f"registered {event.args.iscc} -> {resp.iscc_id} with did {resp.did}")


@click.command()
@click.argument("envfile", default=".env.dev")
def main(envfile):

    # Startup
    log.info(f"load settings from env file {envfile}")
    evm.config = evm.ObserverSettings(_env_file=envfile)

    log.info(f" --> starting evm observer")
    log.info(f"web3:\t\t{evm.config.web3_url}")
    log.info(f"chain:\t{ic.ST_ID(evm.config.chain_id).name}")
    log.info(f"contract:\t{evm.config.hub_contract}")
    log.info(f"registry:\t{evm.config.registry_url}")
    log.info(f"updates:\tevery {evm.config.update_interval} seconds")

    while not evm.chain().w3.isConnected():
        log.error(f"connection failed to {evm.config.web3_url}")
        time.sleep(evm.config.update_interval)

    while True:
        time.sleep(evm.config.update_interval)
        try:
            update()
        except Exception as e:
            if evm.config.sentry_dsn:
                capture_exception(e)
            log.error(e)


if __name__ == "__main__":
    main()

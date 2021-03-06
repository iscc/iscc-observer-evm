# -*- coding: utf-8 -*-
import sys
from asyncio.exceptions import TimeoutError as AsyncTimeoutError
from asyncio.exceptions import IncompleteReadError as AsyncIncompleteReadError
from requests.exceptions import Timeout as RequestsTimeout
from requests.exceptions import ConnectionError as RequestsConnectionError
from requests.exceptions import ReadTimeout as RequestsReadTimeout
import pathlib
import time
import click
import iscc_core as ic
from loguru import logger as log
from sentry_sdk import capture_exception, capture_message

import iscc_observer_evm as evm


HERE = pathlib.Path(__file__).parent.absolute()


def rollback():
    offset = 1
    head = evm.registry().head(offset=offset)
    while True:
        chain_block = evm.chain().block(head.block_height)
        if head.block_hash != chain_block.hash.hex():
            msg = f"registry out of sync at height {head.block_height} hash {head.block_hash}"
            log.warning(msg)
            capture_message(msg)
            offset += 1
            head = evm.registry().head(offset=offset)
        else:
            resp = evm.registry().rollback(head.block_hash)
            if resp:
                msg = f"rolled back to block {resp.block_hash} at height {resp.block_height}"
                log.info(msg)
                capture_message(msg)
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
        log.info(f"new event for {event.args.iscc}")
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
    evm.config = evm.ObserverSettings(_env_file=envfile)

    log.info(f" --> starting evm observer")
    log.info(f"version: {evm.__version__}")
    log.info(f"web3:\t\t{evm.config.web3_provider_uri}")
    log.info(f"chain:\t{ic.ST_ID(evm.config.chain_id).name}")
    log.info(f"contract:\t{evm.config.hub_contract}")
    log.info(f"registry:\t{evm.config.registry_url}")
    log.info(f"updates:\tevery {evm.config.update_interval} seconds")

    while not evm.chain().w3.isConnected():
        log.error(f"connection failed to {evm.config.web3_provider_uri}")
        time.sleep(evm.config.update_interval)

    while True:
        time.sleep(evm.config.update_interval)
        try:
            update()
            evm.timeouts = 0
        except (
            AsyncTimeoutError,
            RequestsTimeout,
            RequestsConnectionError,
            RequestsReadTimeout,
            ValueError,
            AsyncIncompleteReadError,
        ) as e:
            evm.timeouts += 1
            msg = f"{evm.timeouts} consecutive errors"
            log.warning(msg)
            log.warning(e)
            # re-initialize client
            evm.ch = None
            if evm.timeouts > 3:
                capture_exception(e)
        except KeyboardInterrupt:
            sys.exit(0)
        except Exception as e:
            capture_exception(e)


if __name__ == "__main__":
    main()

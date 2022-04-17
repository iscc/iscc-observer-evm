# -*- coding: utf-8 -*-
import time
from loguru import logger as log
import iscc_core as ic
import iscc_observer_evm as evm


def main():
    log.info(f" --> starting evm observer")
    log.info(f"web3:\t\t{evm.config.web3_url}")
    log.info(f"chain:\t\t{ic.ST_ID(evm.config.chain_id).name}")
    log.info(f"contract:\t{evm.config.hub_contract}")
    log.info(f"registry:\t{evm.config.registry_url}")
    log.info(f"updates:\tevery {evm.config.update_interval} seconds")

    while True:
        log.info("observing ...")
        time.sleep(evm.config.update_interval)


if __name__ == "__main__":
    main()

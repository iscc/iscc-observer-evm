"""Registry Client"""
from typing import Optional

import requests
from loguru import logger as log

import iscc_observer_evm as evm
from iscc_observer_evm.models import Head

__all__ = ["registry"]


rc = None


def registry():
    global rc
    if rc is None:
        rc = Registry()
    return rc


class Registry:
    def __init__(self):
        headers = {"Authorization": f"Bearer {evm.config.observer_token}"}
        self.session = requests.Session()
        self.session.headers.update(headers)

    def head(self) -> Optional[Head]:
        url = f"{evm.config.registry_url}/head/{evm.config.chain_id}"
        log.debug(f"GET {url}")
        response = self.session.get(url, timeout=5)
        if response.status_code == 200:
            return Head(**response.json())

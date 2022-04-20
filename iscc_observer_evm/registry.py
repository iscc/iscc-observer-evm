"""Registry Client"""
from typing import Optional

import requests
from loguru import logger as log

import iscc_observer_evm as evm
from iscc_observer_evm.models import Declaration, Head, RegistrationResponse

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
        self.url = evm.config.registry_url
        self.chain_id = evm.config.chain_id
        self.timeout = evm.config.read_timeout

    def head(self, offset: int = 0) -> Optional[Head]:
        url = f"{self.url}/head/{self.chain_id}"
        log.debug(f"GET {url}")
        response = self.session.get(url, timeout=self.timeout, params={"offset": offset})
        if response.status_code == 200:
            return Head(**response.json())
        log.warning(response.content)

    def register(self, declaration: dict) -> RegistrationResponse:
        url = f"{self.url}/register"
        log.debug(f"POST {url}")
        response = self.session.post(url, json=declaration, timeout=self.timeout)
        if response.status_code == 201:
            return RegistrationResponse(**response.json())
        log.warning(response.content)

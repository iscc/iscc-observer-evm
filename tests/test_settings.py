import iscc_observer_evm as evm


def test_evm_config():

    assert evm.config.dict() == {
        "chain_id": 3,
        "hub_contract": "0x23fEcFd850135a6B21c1151ca9a35CC3CB697fd8",
        "observer_token": "observer-token",
        "registry_url": "http://localhost:8888/api",
        "sentry_dsn": "",
        "update_interval": 5,
        "read_timeout": 20,
        "web3_provider_uri": "wss://127.0.0.1:8546",
    }

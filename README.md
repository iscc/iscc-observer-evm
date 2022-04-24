# ISCC - Ethereum Virtual Machine Observer

[![Tests](https://github.com/iscc/iscc-observer-evm/actions/workflows/tests.yml/badge.svg)](https://github.com/iscc/iscc-observer-evm/actions/workflows/tests.yml)

## About `iscc-observer-evm`
`iscc-observer-evm` is a [Python](https://python.org) service for registering declarations of **International Standard Content Codes** ([ISCC](https://iscc.codes)) coming from Web3/EVM compatible blockchains. Instances of this service can observe events from a single [ISCC-HUB contract](https://github.com/iscc/iscc-evm#the-iscc-hub-contract) and register them on an [ISCC Registry](https://github.com/iscc/iscc-registry).

## Configuration

The service is configured via environment variables:

- **`CHAIN_ID`** - ID of blockchain to be observed. [Supported values](https://core.iscc.codes/constants/#iscc_core.constants.ST_ID--st_id) for EVM chains are `ETHEREUM`, `POLYGON`
- **`WEB3_PROVIDER_URI`** - [Web3 Websocket URI](https://web3py.readthedocs.io/en/stable/providers.html#provider-via-environment-variable) used for connecting to blockchain events.
- **`HUB_CONTRACT`** - The address of the [ISCC-HUB contract](https://github.com/iscc/iscc-evm#the-iscc-hub-contract)
- **`REGISTRY_URL`** - URL to OpenAPI REST service of an [ISCC-REGISTRY](https://github.com/iscc/iscc-registry) for event publishing
- **`OBSERVER_TOKEN`** - Bearer secret for authentication with ISCC-REGISTRY API service
- **`UPDATE_INTERVAL`** - Seconds to wait betweenn synchronization of chain-events and the registry
- **`READ_TIMEOUT`** - Timeout for Web3 websocket and REST API https connections in seconds
- **`SENTRY_DSN`** - Optional URI for error notifications via [Sentry](https://sentry.io)

See example at [.env.dev](.env.dev)

## Development
Requirements Python 3.9 with [Poetry](https://python-poetry.org/)
Get started with
```shell
$ git clone https://github.com/iscc/iscc-observer-evm.git
$ cd iscc-observer-evm
$ poetry install
```

Start an observer instance with `poetry run iscc-observer-evm .env.dev`.
You may provide your own .env file configured according to your local development setup.

## Deployment

Docker images for deployment are available via https://ghcr.io/iscc/iscc-observer-evm.
See [docker-compose.yml](docker-compose.yml) for an example of how to deploy multiple observers.


## Maintainers
[@titusz](https://github.com/titusz)

## Contributing

Pull requests are welcome. For significant changes, please open an issue first to discuss your plans. Please make sure to update tests as appropriate.

You may also want join our developer chat on Telegram at <https://t.me/iscc_dev>.

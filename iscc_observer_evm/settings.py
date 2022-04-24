from typing import Optional

import iscc_core as ic
from pydantic import BaseSettings, Field, validator

__all__ = ["config", "ObserverSettings"]


class ObserverSettings(BaseSettings):
    chain_id: ic.ST_ID = Field(..., description="ID of chain to be ovserved")
    web3_provider_uri: str = Field(..., description="WEB3_PROVIDER_URI for chain event monitoring")
    hub_contract: str = Field(..., description="Address of ISCC-HUB contract")
    registry_url: str = Field(..., description="URL of ISCC-REGISTRY service")
    observer_token: str = Field(..., description="OBSERVER_TOKEN for access to ISCC-REGISTRY")
    update_interval: Optional[int] = Field(default=5, description="UPDATE_INTERVAL in seconds")
    read_timeout: Optional[int] = Field(default=20, description="READ_TIMEOUT in seconds")
    sentry_dsn: Optional[str] = Field(default="", description="SENTRY_DSN for error reporting")

    class Config:
        env_file = ".env.dev"
        env_file_encoding = "utf-8"
        use_enum_values = True

    @validator("chain_id", pre=True)
    def chain_id_enum(cls, v):
        if isinstance(v, str):
            return ic.ST_ID[v]
        return ic.ST_ID(v)


config = ObserverSettings()

if config.sentry_dsn:
    import sentry_sdk

    sentry_sdk.init(dsn=config.sentry_dsn, environment=f"observer-{config.chain_id}")

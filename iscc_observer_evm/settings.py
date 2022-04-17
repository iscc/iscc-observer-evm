from typing import Optional
from pydantic import BaseSettings, Field, AnyUrl, validator
import iscc_core as ic

__all__ = [
    "config",
]


class ObserverSettings(BaseSettings):
    chain_id: ic.ST_ID = Field(..., description="ID of chain that is being ovserved")
    web3_url: str = Field(..., description="WEB3_URL for chain event monitoring")
    hub_contract: str = Field(..., description="Address of ISCC-HUB contract")
    registry_url: str = Field(..., description="URL of ISCC-REGISTRY service")
    observer_token: str = Field(..., description="OBSERVER_TOKEN for access to ISCC-REGISTRY")
    update_interval: Optional[int] = Field(default=10, description="UPDATE_INTERVAL in seconds")

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

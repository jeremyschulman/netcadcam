from pydantic import BaseModel, Field


class DeviceDecl(BaseModel):
    hostname: str
    alias: str
    kind: str
    use_interface_maps: list[str] | None = Field(None)
    primary_ip: str

from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict, Field

from .schema import Schema


class Reference(BaseModel):
    ref: Annotated[str, Field(alias="$ref")]

    model_config = ConfigDict(
        validate_by_name=False,
        validate_by_alias=True,
        serialize_by_alias=True,
        extra="forbid",
    )


class Info(BaseModel):
    title: str
    version: str

    model_config = ConfigDict(extra="allow")


class Paths(BaseModel):
    model_config = ConfigDict(extra="allow")


class Components(BaseModel):
    schemas: dict[str, Schema | Reference]

    model_config = ConfigDict(extra="allow")


def supported_version(value: str) -> str:
    error_msg = f"unsupported OpenAPI version ('{value}')"
    parts = value.split(".")
    if len(parts) != 3:
        raise ValueError(error_msg)
    try:
        major, minor, _ = map(int, parts)
    except ValueError as exc:
        raise ValueError(error_msg) from exc
    if (major, minor) != (3, 0):
        raise ValueError(error_msg)
    return value


class OpenAPIObject(BaseModel):
    openapi: Annotated[str, AfterValidator(supported_version)]
    info: Info
    paths: Paths
    components: Components

    model_config = ConfigDict(extra="allow")

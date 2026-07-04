from collections.abc import Iterable
from re import match
from typing import Any

from k8s_model_generator.openapi.schema import Schema
from k8s_model_generator.openapi.v3 import OpenAPIObject, Reference


def to_document_ref(ref: str) -> str:
    if ref == "#/components/schemas/":
        msg = "schema is not specified ('#/components/schemas/<schema>')"
        raise ValueError(msg)
    match_groups = match(r"#/components/schemas/([^/]+)(.*)", ref)
    if match_groups is None:
        return ref
    if len(match_groups[2]) == 0:
        return f"{match_groups[1]}.json"
    return f"{match_groups[1]}.json#{match_groups[2]}"


def update_refs(obj: Any) -> Any:
    match obj:
        case dict():
            if "$ref" in obj:
                obj["$ref"] = to_document_ref(obj["$ref"])
            for item in obj.values():
                update_refs(item)
        case list():
            for item in obj:
                update_refs(item)


def schemas_from_openapi_v3(
    openapi: OpenAPIObject,
) -> Iterable[tuple[str, Schema | Reference]]:
    for name, schema in openapi.components.schemas.items():
        obj = schema.model_dump()
        update_refs(obj)
        schema = type(schema).model_validate(obj)
        yield (f"{name}.json", schema)

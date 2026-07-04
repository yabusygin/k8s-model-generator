from typing import Any

from pytest import mark, raises

from k8s_model_generator.openapi.v3 import OpenAPIObject
from k8s_model_generator.schema_exporter import (
    schemas_from_openapi_v3,
    to_document_ref,
    update_refs,
)


@mark.parametrize(
    argnames=("reference", "expect"),
    argvalues=[
        (
            "#/components/schemas/foo",
            "foo.json",
        ),
        (
            "#/components/schemas/foo/bar",
            "foo.json#/bar",
        ),
        (
            "foo.json",
            "foo.json",
        ),
    ],
)
def test_to_document_ref(reference: str, expect: str) -> None:
    assert to_document_ref(reference) == expect


def test_to_document_ref_value_error() -> None:
    with raises(
        expected_exception=ValueError,
        match=r"^schema is not specified \('#/components/schemas/<schema>'\)$",
    ):
        to_document_ref("#/components/schemas/")


@mark.parametrize(
    argnames=("obj", "fixed"),
    argvalues=[
        (
            {},
            {},
        ),
        (
            {"$ref": "foo.json"},
            {"$ref": "foo.json"},
        ),
        (
            {
                "type": "object",
                "properties": {
                    "$ref": "foo.json",
                },
            },
            {
                "type": "object",
                "properties": {
                    "$ref": "foo.json",
                },
            },
        ),
        (
            {
                "type": "array",
                "items": {
                    "properties": {
                        "foo": {
                            "$ref": "foo.json",
                        },
                    }
                },
            },
            {
                "type": "array",
                "items": {
                    "properties": {
                        "foo": {
                            "$ref": "foo.json",
                        },
                    }
                },
            },
        ),
        (
            {"$ref": "#/components/schemas/foo"},
            {"$ref": "foo.json"},
        ),
        (
            {"$ref": "#/components/schemas/foo/bar"},
            {"$ref": "foo.json#/bar"},
        ),
        (
            {
                "type": "object",
                "properties": {
                    "foo": {
                        "$ref": "#/components/schemas/foo",
                    }
                },
            },
            {
                "type": "object",
                "properties": {
                    "foo": {
                        "$ref": "foo.json",
                    },
                },
            },
        ),
        (
            {
                "type": "array",
                "items": {
                    "properties": {
                        "foo": {
                            "$ref": "#/components/schemas/foo",
                        },
                    }
                },
            },
            {
                "type": "array",
                "items": {
                    "properties": {
                        "foo": {
                            "$ref": "foo.json",
                        },
                    }
                },
            },
        ),
        (
            {
                "allOf": [
                    {
                        "$ref": "#/components/schemas/foo",
                    }
                ],
            },
            {
                "allOf": [
                    {
                        "$ref": "foo.json",
                    }
                ],
            },
        ),
    ],
)
def test_update_refs(obj: Any, fixed: Any) -> None:
    update_refs(obj)
    assert obj == fixed


@mark.parametrize(
    argnames=(
        "schemas",
        "expect",
    ),
    argvalues=[
        (
            {},
            [],
        ),
        (
            {
                "test.Foo": {},
            },
            [
                ("test.Foo.json", {}),
            ],
        ),
        (
            {
                "test.Foo": {"$ref": "#/components/schemas/test.Bar"},
                "test.Bar": {},
            },
            [
                ("test.Foo.json", {"$ref": "test.Bar.json"}),
                ("test.Bar.json", {}),
            ],
        ),
    ],
)
def test_schemas_from_openapi_v3(
    schemas: dict[str, Any], expect: list[tuple[str, dict[str, Any]]]
) -> None:
    openapi = OpenAPIObject.model_validate(
        {
            "openapi": "3.0.0",
            "info": {
                "title": "Kubernetes",
                "version": "unversioned",
            },
            "paths": {},
            "components": {
                "schemas": schemas,
            },
        }
    )
    actual = list(
        map(
            lambda t: (t[0], t[1].model_dump()),
            schemas_from_openapi_v3(openapi),
        )
    )
    assert actual == expect

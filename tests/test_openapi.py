from pathlib import Path

from pydantic import ValidationError
from pytest import mark, raises

from k8s_model_generator.openapi.schema import Schema
from k8s_model_generator.openapi.v3 import (
    Components,
    Info,
    OpenAPIObject,
    Paths,
    Reference,
)

from .conftest import KUBERNETES_OPENAPI_V3_SPEC_FILE_NAMES


@mark.parametrize(
    argnames=("spec_file_name",),
    argvalues=map(
        lambda name: (name,),
        KUBERNETES_OPENAPI_V3_SPEC_FILE_NAMES,
    ),
)
def test_openapi_object_validation(
    kubernetes_openapi_v3_spec_dir: Path, spec_file_name: str
) -> None:
    spec_file = Path(kubernetes_openapi_v3_spec_dir, spec_file_name)
    OpenAPIObject.model_validate_json(spec_file.read_text(encoding="utf-8"))


@mark.parametrize(
    argnames=("version",),
    argvalues=[
        ("3.0.0",),
        ("3.0.1",),
    ],
)
def test_openapi_version(version: str) -> None:
    OpenAPIObject.model_validate(
        {
            "openapi": version,
            "info": {
                "title": "Kubernetes",
                "version": "unversioned",
            },
            "paths": {},
            "components": {
                "schemas": {},
            },
        }
    )


@mark.parametrize(
    argnames=("version",),
    argvalues=[
        ("",),
        ("3",),
        ("3.0",),
        ("3.0.0.0",),
        ("2.0.0",),
        ("4.0.0",),
        ("3.1.0",),
        ("3.0.0pre1",),
    ],
)
def test_unsupported_openapi_version(version: str) -> None:
    with raises(ValidationError) as exc:
        OpenAPIObject.model_validate(
            {
                "openapi": version,
                "info": {
                    "title": "Kubernetes",
                    "version": "unversioned",
                },
                "paths": {},
                "components": {
                    "schemas": {},
                },
            }
        )
    assert any(
        map(
            lambda e: (
                e["type"] == "value_error"
                and f"unsupported OpenAPI version ('{version}')" in e["msg"]
            ),
            exc.value.errors(),
        )
    )


@mark.parametrize(
    argnames=("ref",),
    argvalues=[
        ("#/components/schemas/foo",),
        ("#/components/schemas/foo/bar",),
    ],
)
def test_internal_reference(ref: str) -> None:
    Reference.model_validate({"$ref": ref})


def test_ref_alias() -> None:
    with raises(ValidationError):
        Reference.model_validate(
            {
                "ref": "#/components/schemas/foo",
            }
        )

    obj = {
        "$ref": "#/components/schemas/foo",
    }
    assert Reference.model_validate(obj).model_dump() == obj


def test_openapi_object_extra_fields() -> None:
    obj = {
        "openapi": "3.0.0",
        "info": {
            "title": "Kubernetes",
            "version": "unversioned",
        },
        "paths": {},
        "components": {
            "schemas": {},
        },
        "test-extra-field": "test-extra-value",
    }
    assert OpenAPIObject.model_validate(obj).model_dump() == obj


def test_info_extra_fields() -> None:
    obj = {
        "title": "Kubernetes",
        "version": "unversioned",
        "test-extra-field": "test-extra-value",
    }
    assert Info.model_validate(obj).model_dump() == obj


def test_paths_extra_fields() -> None:
    obj = {
        "test-extra-field": "test-extra-value",
    }
    assert Paths.model_validate(obj).model_dump() == obj


def test_components_extra_fields() -> None:
    obj = {
        "schemas": {},
        "test-extra-field": "test-extra-value",
    }
    assert Components.model_validate(obj).model_dump() == obj


def test_reference_extra_fields() -> None:
    with raises(ValidationError) as exc:
        Reference.model_validate(
            {
                "$ref": "#/components/schemas/foo",
                "test-extra-field": "test-extra-value",
            }
        )
    assert any(
        map(
            lambda e: (
                e["type"] == "extra_forbidden" and e["loc"] == ("test-extra-field",)
            ),
            exc.value.errors(),
        )
    )


def test_schema_extra_fields() -> None:
    obj = {
        "test-extra-field": "test-extra-value",
    }
    assert Schema.model_validate(obj).model_dump() == obj

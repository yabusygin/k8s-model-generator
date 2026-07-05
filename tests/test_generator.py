from importlib import import_module
from json import dumps, loads
from pathlib import Path
from typing import Any

from pydantic import BaseModel
from pytest import fixture, mark

from k8s_model_generator.generator import generate, preprocess_input, preprocess_schema

from .utils import create_package


def test_generate(kubernetes_openapi_v3_spec_dir: Path, sys_path_dir: Path) -> None:
    input_file = Path(kubernetes_openapi_v3_spec_dir, "api__v1_openapi.json")
    output_dir = create_package("testmodels", sys_path_dir)
    generate(input_file, output_dir)
    v1 = import_module("testmodels.io.k8s.api.core.v1")
    assert issubclass(v1.Pod, BaseModel)


@mark.parametrize(
    argnames=("title", "schema", "preprocessed"),
    argvalues=[
        (
            "io.k8s.apimachinery.pkg.util.intstr.IntOrString",
            {
                "format": "int-or-string",
                "oneOf": [
                    {"type": "integer"},
                    {"type": "string"},
                ],
            },
            {
                "oneOf": [
                    {"type": "integer"},
                    {"type": "string"},
                ],
            },
        )
    ],
)
def test_preprocess_schema(
    title: str, schema: dict[str, Any], preprocessed: dict[str, Any]
) -> None:
    preprocess_schema(title, schema)
    assert schema == preprocessed


@fixture
def input_dir(tmp_path: Path) -> Path:
    _input_dir = Path(tmp_path, "input")
    _input_dir.mkdir()
    return _input_dir


@fixture
def preprocessed_file(tmp_path: Path) -> Path:
    return Path(tmp_path, "preprocessed_openapi.json")


@mark.parametrize(
    argnames=("input_openapis", "preprocessed_openapi"),
    argvalues=[
        (
            [
                {
                    "openapi": "3.0.0",
                    "info": {
                        "title": "Kubernetes",
                        "version": "unversioned",
                    },
                    "paths": {},
                    "components": {
                        "schemas": {
                            "io.k8s.apimachinery.pkg.util.intstr.IntOrString": {
                                "format": "int-or-string",
                                "oneOf": [
                                    {"type": "integer"},
                                    {"type": "string"},
                                ],
                            }
                        },
                    },
                },
            ],
            {
                "openapi": "3.0.0",
                "info": {
                    "title": "k8s-model-generator",
                    "version": "unversioned",
                },
                "paths": {},
                "components": {
                    "schemas": {
                        "io.k8s.apimachinery.pkg.util.intstr.IntOrString": {
                            "oneOf": [
                                {"type": "integer"},
                                {"type": "string"},
                            ],
                        }
                    },
                },
            },
        ),
        (
            [
                {
                    "openapi": "3.0.0",
                    "info": {
                        "title": "Kubernetes",
                        "version": "unversioned",
                    },
                    "paths": {},
                    "components": {
                        "schemas": {
                            "test.Foo": {
                                "type": "object",
                                "properties": {
                                    "foo1": {
                                        "type": "string",
                                    }
                                },
                            }
                        },
                    },
                },
                {
                    "openapi": "3.0.0",
                    "info": {
                        "title": "Kubernetes",
                        "version": "unversioned",
                    },
                    "paths": {},
                    "components": {
                        "schemas": {
                            "test.Foo": {
                                "type": "object",
                                "properties": {
                                    "foo2": {
                                        "type": "string",
                                    }
                                },
                            },
                            "test.Bar": {
                                "type": "object",
                                "properties": {
                                    "bar": {
                                        "type": "string",
                                    }
                                },
                            },
                        },
                    },
                },
            ],
            {
                "openapi": "3.0.0",
                "info": {
                    "title": "k8s-model-generator",
                    "version": "unversioned",
                },
                "paths": {},
                "components": {
                    "schemas": {
                        "test.Foo": {
                            "type": "object",
                            "properties": {
                                "foo1": {
                                    "type": "string",
                                }
                            },
                        },
                        "test.Bar": {
                            "type": "object",
                            "properties": {
                                "bar": {
                                    "type": "string",
                                }
                            },
                        },
                    },
                },
            },
        ),
    ],
)
def test_preprocess_input(
    input_openapis: list[dict[str, Any]],
    input_dir: Path,
    preprocessed_file: Path,
    preprocessed_openapi: dict[str, Any],
) -> None:
    input_files: list[Path] = []
    for i, input_openapi in enumerate(input_openapis):
        input_file = Path(input_dir, f"{i}_openapi.json")
        input_file.write_text(dumps(input_openapi))
        input_files.append(input_file)
    preprocess_input(input_files, preprocessed_file)
    assert loads(preprocessed_file.read_text()) == preprocessed_openapi

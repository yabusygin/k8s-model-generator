from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from datamodel_code_generator import (
    generate as _generate,
)
from datamodel_code_generator.config import GenerateConfig
from datamodel_code_generator.enums import DataModelType, InputFileType

from k8s_model_generator.openapi.v3 import OpenAPIObject


def fix_int_or_string_warnings(schema: dict[str, Any]) -> None:
    """Fix warnings about unknown 'int-or-string' format.

    Fix 'datamodel-code-generator' warnings about unknown 'int-or-string' format:

    * UserWarning: format of 'int-or-string' not understood for 'integer' - using
      default
    * UserWarning: format of 'int-or-string' not understood for 'string' - using
      default
    """
    if "format" in schema and schema["format"] == "int-or-string":
        schema.pop("format")


def preprocess_schema(title: str, schema: dict[str, Any]) -> None:
    if title == "io.k8s.apimachinery.pkg.util.intstr.IntOrString":
        fix_int_or_string_warnings(schema)


def preprocess_input(input_file: Path, preprocessed_file: Path) -> None:
    schemas: dict[str, dict[str, Any]] = {}
    openapi = OpenAPIObject.model_validate_json(input_file.read_text(encoding="utf-8"))
    for title, schema in map(
        lambda item: (item[0], item[1].model_dump(mode="json")),
        openapi.components.schemas.items(),
    ):
        preprocess_schema(title, schema)
        schemas[title] = schema
    preprocessed_openapi = OpenAPIObject.model_validate(
        {
            "openapi": "3.0.0",
            "info": {
                "title": "k8s-model-generator",
                "version": "unversioned",
            },
            "paths": {},
            "components": {
                "schemas": schemas,
            },
        }
    )
    preprocessed_file.write_text(
        data=preprocessed_openapi.model_dump_json(ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def generate(input_file: Path, output_dir: Path) -> None:
    with TemporaryDirectory() as tmp_dir:
        preprocessed_file = Path(tmp_dir, input_file.name)
        preprocess_input(input_file, preprocessed_file)
        _generate(
            input_=preprocessed_file,
            config=GenerateConfig(
                input_file_type=InputFileType.OpenAPI,
                output_model_type=DataModelType.PydanticV2BaseModel,
                output=output_dir,
            ),
        )

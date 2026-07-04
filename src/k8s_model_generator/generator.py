from pathlib import Path

from datamodel_code_generator import (
    generate as _generate,
)
from datamodel_code_generator.config import GenerateConfig
from datamodel_code_generator.enums import DataModelType, InputFileType


def generate(input_file: Path, output_dir: Path) -> None:
    _generate(
        input_=input_file,
        config=GenerateConfig(
            input_file_type=InputFileType.OpenAPI,
            output_model_type=DataModelType.PydanticV2BaseModel,
            output=output_dir,
        ),
    )

from typing import Any, List, Dict
from langflow.custom import Component
from langflow.field_typing.range_spec import RangeSpec
from langflow.inputs.inputs import (
    DataInput,
    IntInput,
    MessageTextInput,
)
from langflow.io import Output
from langflow.schema import Data
from langflow.schema.dotdict import dotdict


class UpdateDataComponent(Component):
    display_name: str = "File Field Extraction"
    description: str = "Get data from files by fields"
    name: str = "UpdateData"
    MAX_FIELDS = 15  
    icon = "FolderSync"

    inputs = [
        DataInput(
            name="paths",
            display_name="File Paths",
            info="List of file paths to process.",
            is_list=True,  
            required=True,
        ),
        IntInput(
            name="number_of_fields",
            display_name="Number of Fields",
            info="Number of fields to be added to the record.",
            real_time_refresh=True,
            value=0,
            range_spec=RangeSpec(min=1, max=MAX_FIELDS, step=1, step_type="int"),
        ),
    ]

    outputs = [
        Output(display_name="Data", name="dict_list", method="build_data"),
    ]

    def update_build_config(self, build_config: dotdict, field_value: Any, field_name: str | None = None):
        """Update the build configuration when the number of fields changes."""
        if field_name == "number_of_fields":
            default_keys = {
                "code",
                "_type",
                "number_of_fields",
                "paths",
            }
            try:
                field_value_int = int(field_value)
            except ValueError:
                return build_config

            if field_value_int > self.MAX_FIELDS:
                build_config["number_of_fields"]["value"] = self.MAX_FIELDS
                msg = f"Number of fields cannot exceed {self.MAX_FIELDS}."
                raise ValueError(msg)

            existing_fields = {}

            for key in list(build_config.keys()):
                if key not in default_keys:
                    existing_fields[key] = build_config.pop(key)

            for i in range(1, field_value_int + 1):
                key = f"field_{i}_name"
                if key in existing_fields:
                    field = existing_fields[key]
                    build_config[key] = field
                else:
                    field = MessageTextInput(
                        display_name=f"Field {i} Name",
                        name=key,
                        info=f"Name of field {i}.",
                    )
                    build_config[field.name] = field.to_dict()

            build_config["number_of_fields"]["value"] = field_value_int
        return build_config



        
    def get_field_names(self) -> List[str]:
        """Get the list of field names from the component's attributes."""
        field_names = []
        for i in range(1, self.number_of_fields + 1):
            field_name = self._attributes.get(f"field_{i}_name")
            if field_name:
                field_names.append(field_name)
        return field_names

    def process_file(self, file_path: str, field_names: List[str]) -> Dict[str, Any]:
        """Process the file and extract data based on the provided field names."""
        data = []
        builder = docbuilder.CDocBuilder()
        try:
            builder.OpenFile(
                file_path,
                "<m_nCsvTxtEncoding>0</m_nCsvTxtEncoding><m_nCsvDelimiter>0</m_nCsvDelimiter>"
            )
            context = builder.GetContext()
            globalObj = context.GetGlobal()
            api = globalObj["Api"]
            document = api.Call("GetDocument")

            length = document.Call("GetElementsCount").ToInt()
            record = {}
            for i in range(length):
                paragraph = document.Call("GetElement", i)
                contentControls = paragraph.Call("GetAllContentControls")
                controlLength = contentControls.GetLength()

                
                for j in range(controlLength):
                    control = contentControls.Get(j)
                    tag = control.Call("GetTag").ToString()
                    text = control.Call("GetElement", 0).Call("GetText").ToString()

                    if tag in field_names:
                        record[tag] = text
                    


        except Exception as e:
            print(f"Ошибка при обработке файла '{file_path}': {e}")
        finally:
            builder.CloseFile()

        return record
        
    def get_text_from_processed_data(self, processed_data: List[str]) -> str:
        """Convert processed_data into a readable text format."""
        text_lines = []
        for person in processed_data:
            for key, record in person.items():
                text_lines.append(f"  {key}: {record}")
                text_lines.append("")

        return '\n'.join(text_lines)
        
        
    def build_data(self) -> Data:
        """Process files and return extracted data."""
        file_paths = self.paths
        field_names = self.get_field_names()
        processed_data = []

        for file_path in file_paths:
            if isinstance(file_path, Data):
                file_path = file_path.text  
            file_data = self.process_file(file_path, field_names)
            processed_data.append(file_data)
        return Data(data={"items": processed_data})

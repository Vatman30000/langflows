from typing import Any, List, Dict
from langflow.custom import Component
from langflow.field_typing.range_spec import RangeSpec
from langflow.io import (
    BoolInput,
    DataInput,
    DictInput,
    IntInput,
    MessageTextInput,
    HandleInput,
    DropdownInput
)
from langflow.io import Output
from langflow.schema import Data
from langflow.schema.dotdict import dotdict
import docbuilder
from datetime import datetime

class UpdateDataComponent(Component):
    display_name: str = "Filter Component"
    description: str = "filter data"
    name: str = "FilterData"
    MAX_FIELDS = 15  
    icon = "filter"

    inputs = [
        DataInput( 
            name="dict_list",
            display_name="Data",
            info="List of dictionaries to process.",
            input_types=["Data"],
            required=True,
        ),
        DropdownInput(
            name="type_of_operation",
            display_name="Operation type",
            real_time_refresh=True,
            info="File types to load. Select one or more types or leave empty to load all supported types.",
            options=["Insert","<",">"],
            value=[],
        ),
        DropdownInput(
            name="type_of_input",
            display_name="Input type",
            info="File types to load. Select one or more types or leave empty to load all supported types.",
            options=["date","money"],
            value=[],
        ),
    ]

    outputs = [
        Output(display_name="Data", name="data", method="build_data"),
    ]
    
    def update_build_config(self, build_config: dotdict, field_value: Any, field_name: str | None = None):
        """Update the build configuration based on the selected operation."""
        if field_name == "type_of_operation":
            default_keys = {
                "code",
                "_type",
                "dict_list",
                "type_of_input",
                "type_of_operation",
            }


            type_of_operation = build_config.get("type_of_operation", {}).get("value", [])
            if type_of_operation:
                operation = type_of_operation
                if operation == "Insert":
                    num_fields = 2
                elif operation == "<":
                    num_fields = 1
                elif operation == ">":
                    num_fields = 1
                else:
                    num_fields = 0 
            else:
                num_fields = 0

            existing_fields = {}

            
            for key in list(build_config.keys()):
                if key not in default_keys:
                    existing_fields[key] = build_config.pop(key)

            
            for i in range(1, num_fields + 1):
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
        return build_config

    def build_data(self) -> Data:
        """Process the list of dictionaries."""
        dict_list = self.dict_list.data.get("items", [])
        dates = self.get_field_names()
        if self.type_of_operation == "Insert":
            filtered_dict_list = self.filter_vacation_data(dict_list, dates[0], dates[1])
        else:
            filtered_dict_list = self.filter_vacation_data(dict_list, dates[0])
        return self.get_text_from_processed_data(filtered_dict_list) 
        
    def get_field_names(self) -> List[str]:
        """Get the list of field names from the component's attributes."""
        field_names = []
        for key, value in self._attributes.items():
            if key.startswith("field_") and key.endswith("_name"):
                field_names.append(value)
        return field_names
        
    def get_text_from_processed_data(self, processed_data: List[str]) -> str:
        """Convert processed_data into a readable text format."""
        text_lines = []
        for person in processed_data:
            for key, record in person.items():
                text_lines.append(f"  {key}: {record}")
                text_lines.append("")
        
        return '\n'.join(text_lines)
    
    
    def filter_vacation_data(self, vacation_data: List[Dict[str, Any]], *dates: str) -> List[Dict[str, Any]]:
        filtered_data = []
        operation = self.type_of_operation if self.type_of_operation else ""
        
        try:
            if operation == "Insert":
                start_date = datetime.strptime(dates[0], "%d-%m-%Y")
                end_date = datetime.strptime(dates[1], "%d-%m-%Y")
            else:
                compare_date = datetime.strptime(dates[0], "%d-%m-%Y")
        except ValueError as e:
            raise ValueError(f"Invalid date format. Error: {e}")
    
        for person in vacation_data:
            try:
                vacation_start = datetime.strptime(person["start_date"], "%d-%m-%Y")
                vacation_end = datetime.strptime(person["end_date"], "%d-%m-%Y")
                
                
                if operation == "Insert":
                    if (vacation_start <= end_date) and (vacation_end >= start_date):
                        filtered_data.append(person)
                elif operation == "<":
                    if  vacation_end < compare_date:
                        filtered_data.append(person)
                elif operation == ">":
                    if  vacation_start > compare_date:
                        filtered_data.append(person)
                        
            except ValueError as e:
                print(f"Error parsing vacation dates for {person}: {e}")
                continue
    
        return filtered_data
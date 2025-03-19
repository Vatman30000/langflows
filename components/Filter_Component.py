from typing import Any, List, Dict
from langflow.custom import Component
from langflow.field_typing.range_spec import RangeSpec
from langflow.inputs.inputs import (
    BoolInput,
    DataInput,
    DictInput,
    IntInput,
    MessageTextInput,
    HandleInput
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
    ]

    outputs = [
        Output(display_name="Data", name="data", method="build_data"),
    ]

    def build_data(self) -> Data:
        """Process the list of dictionaries."""
        dict_list = self.dict_list.data.get("items", [])
        filtered_dict_list = self.filter_vacation_data(dict_list, start_date='01-01-2023',end_date='31-12-2023')
        return self.get_text_from_processed_data(filtered_dict_list) 
        
    def get_text_from_processed_data(self, processed_data: List[str]) -> str:
        """Convert processed_data into a readable text format."""
        text_lines = []
        for person in processed_data:
            for key, record in person.items():
                text_lines.append(f"  {key}: {record}")
                text_lines.append("")
        
        return '\n'.join(text_lines)
    
    
    def filter_vacation_data(self, vacation_data: List[Dict[str, Any]], start_date: str, end_date: str) -> List[Dict[str, Any]]:
        filtered_data = []
        try:
            start_date = datetime.strptime(start_date, "%d-%m-%Y")
            end_date = datetime.strptime(end_date, "%d-%m-%Y")
        except ValueError as e:
            msg = f"Invalid date format. Error: {e}"
            raise ValueError(msg)

    
        for person in vacation_data:
            try:
                vacation_start = datetime.strptime(person["start_date"], "%d-%m-%Y")
                vacation_end = datetime.strptime(person["end_date"], "%d-%m-%Y")
            except ValueError as e:
                msg = f"Error parsing vacation dates for {person}: {e}"
                print(msg)
                continue
    
            if (vacation_start <= end_date) and (vacation_end >= start_date):
                filtered_data.append(person)
    
        return filtered_data
from typing import Any, List, Dict
from langflow.custom import Component
from langflow.field_typing.range_spec import RangeSpec
from langflow.inputs.inputs import (
    BoolInput,
    DataInput,
    DictInput,
    IntInput,
    MessageTextInput,
)
from langflow.io import Output
from langflow.schema import Data
from langflow.schema.dotdict import dotdict
import docbuilder


class UpdateDataComponent(Component):
    display_name: str = "Filter Component"
    description: str = "Get data from files by fields"
    name: str = "FilterData"
    MAX_FIELDS = 15  
    icon = "filter"

    inputs = [
        DataInput( 
            name="dict_list",
            display_name="Dict List",
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
        dict_list = self.dict_list
        if isinstance(dict_list, Data):
            dict_list = dict_list.data.get("items", [])  
        return Data(data={"items": dict_list})  

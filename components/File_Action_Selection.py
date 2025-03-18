# from langflow.field_typing import Data
from langflow.custom import Component
from langflow.io import MessageTextInput, Output
from langflow.schema import Data


class CustomComponent(Component):
    display_name = "File Action Selection"
    description = "Use as a template to create your own component."
    documentation: str = "https://docs.langflow.org/components-custom-components"
    icon = "split"
    name = "File Action Selector"

    inputs = [
        HandleInput(
            name="input_value",
            display_name="Paths",
            info="Message to be passed as output.",
            input_types=["Data"],
            required=True,
        ),
        MultiselectInput(
            name="types",
            display_name="File Types",
            info="File types to load. Select one or more types or leave empty to load all supported types.",
            options=["File Field Extractor"],
            value=[],
        ),
    ]

    outputs = [
        Output(display_name="Output", name="output", method="build_output"),
    ]
    # поменять логику
    def build_output(self) -> Data:
        data = Data(value=self.input_value)
        self.status = data
        
        return self.input_value


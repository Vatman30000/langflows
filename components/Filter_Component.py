from datetime import datetime
from typing import Any

from langflow.custom import Component
from langflow.io import DataInput, DropdownInput, MessageTextInput, Output
from langflow.schema import Data
from langflow.schema.dotdict import dotdict


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
            real_time_refresh=True,
            value=[],
        ),
    ]

    outputs = [
        Output(display_name="Data", name="data", method="build_data"),
    ]

    def update_build_config(self, build_config: dotdict, field_value: Any, field_name: str | None = None)-> dotdict:
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



    def get_field_names(self) -> list[str]:
        """Get the list of field names from the component's attributes."""
        field_names = []
        for key, value in self._attributes.items():
            if key.startswith("field_") and key.endswith("_name"):
                field_names.append(value)
        return field_names

    def get_text_from_processed_data(self, processed_data: list[str]) -> str:
        """Convert processed_data into a readable text format."""
        text_lines = []
        for person in processed_data:
            for key, record in person.items():
                text_lines.append(f"  {key}: {record}")
                text_lines.append("")

        return "\n".join(text_lines)



    def filter_vacation_data(self, vacation_data: list[dict[str, Any]], *dates: str) -> list[dict[str, Any]]:
        """Filter vacation data based on operation type and dates."""
        if not self.type_of_operation:
            return []

        operation = self.type_of_operation
        try:
            parsed_dates = self._parse_dates(operation, *dates)
        except ValueError as e:
            raise ValueError(f"Invalid date format. Error: {e}") from e

        return [
            person for person in vacation_data
            if self._should_include_person(person, operation, parsed_dates)
        ]

    def _parse_dates(self, operation: str, *dates: str) -> tuple:
        """Parse input dates based on operation type."""
        if operation == "Insert":
            if len(dates) < 2:
                raise ValueError("Insert operation requires 2 dates")
            return (
                datetime.strptime(dates[0], "%d-%m-%Y"),
                datetime.strptime(dates[1], "%d-%m-%Y")
            )
        else:
            if not dates:
                raise ValueError("Comparison operation requires at least 1 date")
            return (datetime.strptime(dates[0], "%d-%m-%Y"),)

    def _should_include_person(self, person: dict, operation: str, parsed_dates: tuple) -> bool:
        """Determine if person should be included in filtered results."""
        try:
            if operation == "Insert":
                start_date, end_date = parsed_dates
                vacation_start = datetime.strptime(person["start_date"], "%d-%m-%Y")
                vacation_end = datetime.strptime(person["end_date"], "%d-%m-%Y")
                return (vacation_start <= end_date) and (vacation_end >= start_date)

            elif operation == "<":
                compare_date = parsed_dates[0]
                vacation_end = datetime.strptime(person["end_date"], "%d-%m-%Y")
                return vacation_end < compare_date

            elif operation == ">":
                compare_date = parsed_dates[0]
                vacation_start = datetime.strptime(person["start_date"], "%d-%m-%Y")
                return vacation_start > compare_date

        except ValueError as e:
            self.log(f"Error parsing vacation dates for {person}: {e}")
            return False

        return False

    def filter_money_data(self, money_data: list[dict[str, Any]], *amounts: int) -> list[dict[str, Any]]:
        """Filter money data based on operation type and amounts."""
        if not self.type_of_operation:
            return []

        operation = self.type_of_operation
        try:
            parsed_amounts = self._parse_amounts(operation, *amounts)
        except ValueError as e:
            raise ValueError(f"Invalid amount format. Error: {e}") from e

        return [
            person for person in money_data
            if self._should_include_item(person, operation, parsed_amounts)
        ]

    def _parse_amounts(self, operation: str, *amounts: int) -> tuple:
        """Parse input amounts based on operation type."""
        if operation == "Insert":
            if len(amounts) < 2:
                raise ValueError("Insert operation requires 2 amounts")
            return [int(amounts[0]), int(amounts[1])]
        else:
            if not amounts:
                raise ValueError("Comparison operation requires at least 1 amount")
            return [int(amounts[0])]

    def _should_include_item(self, person: dict, operation: str, parsed_amounts: list) -> bool:
        """Determine if item should be included in filtered results."""
        try:


            if operation == "Insert":
                start_money = int(person["start_money"].replace(".", ""))
                end_money = int(person["end_money"].replace(".", ""))
                min_amount, max_amount = parsed_amounts
                return start_money <= min_amount and max_amount <= end_money

            elif operation == "<":
                start_money = int(person["start_money"].replace(".", ""))
                return start_money < parsed_amounts[0]

            elif operation == ">":

                return end_money > parsed_amounts[0]

        except (ValueError, KeyError) as e:
            self.log(f"Error parsing money amount for {person}: {e}")
            return False

        return False

    def build_data(self) -> Data:
        """Process the list of dictionaries."""
        dict_list = self.dict_list.data.get("items", [])
        fields = self.get_field_names()
        if self.type_of_input =="date":
            dates_to_pass = fields[:2] if self.type_of_operation == "Insert" else fields[:1]
            filtered_dict_list = self.filter_vacation_data(dict_list, *dates_to_pass)
        elif self.type_of_input == "money":
            money_to_pass = fields[:2] if self.type_of_operation == "Insert" else fields[:1]
            filtered_dict_list = self.filter_money_data(dict_list, *money_to_pass)
        return self.get_text_from_processed_data(filtered_dict_list)

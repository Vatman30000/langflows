from langflow.base.data.utils import TEXT_FILE_TYPES, parallel_load_data, parse_text_file_to_data, retrieve_file_paths
from langflow.custom import Component
from langflow.io import BoolInput, IntInput, MessageTextInput, MultiselectInput
from langflow.schema import Data
from langflow.schema.dataframe import DataFrame
from langflow.template import Output
from collections import defaultdict
import docbuilder
from datetime import datetime

TEXT_FILE_TYPES.extend([".docx", ".pdf"])

class DirectoryComponent(Component):
    display_name = "Directory"
    description = "Recursively load files from a directory and extract vacation data within a date range."
    icon = "folder"
    name = "Directory"

    inputs = [
        MessageTextInput(
            name="path",
            display_name="Path",
            info="Path to the directory to load files from. Defaults to current directory ('.')",
            value=".",
            tool_mode=True,
        ),
        MessageTextInput(
            name="start_date",
            display_name="Start Date",
            info="Start date of the range (format: YYYY-MM-DD).",
            value="2023-01-01",
        ),
        MessageTextInput(
            name="end_date",
            display_name="End Date",
            info="End date of the range (format: YYYY-MM-DD).",
            value="2023-12-31",
        ),
        MultiselectInput(
            name="types",
            display_name="File Types",
            advanced=True,
            info="File types to load. Select one or more types or leave empty to load all supported types.",
            options=TEXT_FILE_TYPES,
            value=[],
        ),
        IntInput(
            name="depth",
            display_name="Depth",
            advanced=True,
            info="Depth to search for files.",
            value=0,
        ),
        IntInput(
            name="max_concurrency",
            display_name="Max Concurrency",
            advanced=True,
            info="Maximum concurrency for loading files.",
            value=2,
        ),
        BoolInput(
            name="load_hidden",
            display_name="Load Hidden",
            advanced=True,
            info="If true, hidden files will be loaded.",
        ),
        BoolInput(
            name="recursive",
            display_name="Recursive",
            advanced=True,
            info="If true, the search will be recursive.",
        ),
        BoolInput(
            name="silent_errors",
            display_name="Silent Errors",
            advanced=True,
            info="If true, errors will not raise an exception.",
        ),
        BoolInput(
            name="use_multithreading",
            display_name="Use Multithreading",
            advanced=True,
            info="If true, multithreading will be used.",
        ),
    ]

    outputs = [
        Output(display_name="Data", name="data", method="load_directory"),
    ]

    def process_file(self, file_path: str) -> dict:
        vacation_data = {}
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
            
            person_name = None
            start_vacation = None
            end_vacation = None

            for i in range(length):
                paragraph = document.Call("GetElement", i)
                contentControls = paragraph.Call("GetAllContentControls")
                controlLength = contentControls.GetLength()

                for j in range(controlLength):
                    control = contentControls.Get(j)
                    tag = control.Call("GetTag").ToString()
                    text = control.Call("GetElement", 0).Call("GetText").ToString()

                    if tag == "person":
                        person_name = text
                    elif tag == "start_date":
                        start_vacation = text
                    elif tag == "end_date":
                        end_vacation = text

                if person_name and start_vacation and end_vacation:
                    vacation_data[person_name] = [start_vacation, end_vacation]

        except Exception as e:
            print(f"Ошибка при обработке файла '{file_path}': {e}")
        finally:
            builder.CloseFile()

        return vacation_data

    def filter_vacation_data(self, vacation_data: dict, start_date: str, end_date: str) -> dict:
        filtered_data = {}
        try:
            start_date = datetime.strptime(start_date, "%d-%m-%Y")
            end_date = datetime.strptime(end_date, "%d-%m-%Y")
        except ValueError as e:
            raise ValueError(f"Неверный формат даты. Ошибка: {e}")
    
        for person, dates_list in vacation_data.items():
            for dates in dates_list:
                try:
                    vacation_start = datetime.strptime(dates[0], "%d-%m-%Y")
                    vacation_end = datetime.strptime(dates[1], "%d-%m-%Y")
                except ValueError as e:
                    print(f"Ошибка при парсинге дат отпуска для {person}: {dates}. Ошибка: {e}")
                    continue
    
                if (vacation_start <= end_date) and (vacation_end >= start_date):
                    if person not in filtered_data:
                        filtered_data[person] = []
                    filtered_data[person].append(dates)
    
        return filtered_data

    def load_directory(self) -> list[Data]:
        path = self.path
        start_date = self.start_date
        end_date = self.end_date
        types = self.types
        depth = self.depth
        max_concurrency = self.max_concurrency
        load_hidden = self.load_hidden
        recursive = self.recursive
        silent_errors = self.silent_errors
        use_multithreading = self.use_multithreading

        resolved_path = self.resolve_path(path)

        if not types:
            types = TEXT_FILE_TYPES

        invalid_types = [t for t in types if t not in TEXT_FILE_TYPES]
        if invalid_types:
            msg = f"Invalid file types specified: {invalid_types}. Valid types are: {TEXT_FILE_TYPES}"
            raise ValueError(msg)

        valid_types = types

        file_paths = retrieve_file_paths(
            resolved_path, load_hidden=load_hidden, recursive=recursive, depth=depth, types=valid_types
        )

        all_vacation_data = defaultdict(list)
        for file_path in file_paths:
            vacation_data = self.process_file(file_path)
            for person, dates in vacation_data.items():
                all_vacation_data[person].append(dates)

        filtered_data = self.filter_vacation_data(all_vacation_data, start_date, end_date)

        result = []
        for person, dates_list in filtered_data.items():
            for dates in dates_list:
                data = Data(
                    text=f"{person}: {dates[0]} - {dates[1]}\n",
                    metadata={"person": person, "start_date": dates[0], "end_date": dates[1]}
                )
                result.append(data)

        return result

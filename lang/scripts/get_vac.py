import os
import docbuilder

def get_file_paths(folder_path: str) -> list:
    file_paths = []
    
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".pdf") or file.endswith(".docx"):
                file_path = os.path.join(root, file)
                file_paths.append(file_path)
                
    return file_paths

folder_path = r"/home/alexandr/Yandex.Disk/pyprojects/langflow/lang/source/office_vacation"  
file_paths = get_file_paths(folder_path)

all_vacation_data = {}

builder = docbuilder.CDocBuilder()

for file_path in file_paths:
    print(f"Обрабатывается файл: {file_path}")

    if not os.path.exists(file_path):
        print(f"Файл '{file_path}' не найден.")
        continue

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
        
        vacation_data = {}

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

        for person, dates in vacation_data.items():
            if person in all_vacation_data:
                all_vacation_data[person].append(dates)
            else:
                all_vacation_data[person] = [dates]

    except Exception as e:
        print(f"Произошла ошибка при обработке файла '{file_path}': {e}")
    finally:
        builder.CloseFile()

print(all_vacation_data)
print("\nРезультат обработки всех файлов:")
for person, dates_list in all_vacation_data.items():
    print(f"{person}:")
    for dates in dates_list:
        print(f"  Начало отпуска: {dates[0]}, Окончание отпуска: {dates[1]}")
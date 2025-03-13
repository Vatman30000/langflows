import os
import docbuilder

folder_path = r"/home/alexandr/Yandex.Disk/pyprojects/langflow/lang/source/office_vacation"  

def get_file_paths(folder_path: str)-> list:
    file_paths = []
    
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".pdf") or file.endswith(".docx"):
                file_path = os.path.join(root, file)
                file_paths.append(file_path)
                
    return file_paths


def gef_persons_dict(folder_path: str)-> dict:
    file_paths = get_file_paths(folder_path)

    for path in file_paths:
        print(path)

    builder = docbuilder.CDocBuilder()


    if not os.path.exists(path):
        raise FileNotFoundError(f"Файл '{path}' не найден.")

    try:
        builder.OpenFile(
            path,
            "<m_nCsvTxtEncoding>0</m_nCsvTxtEncoding><m_nCsvDelimiter>0</m_nCsvDelimiter>"
            )

        context = builder.GetContext()

        globalObj = context.GetGlobal()

        api = globalObj["Api"]
        document = api.Call("GetDocument")

        length = document.Call("GetElementsCount").ToInt()
        for i in range(length):
            paragraph = document.Call("GetElement", i)
            contentControls = paragraph.Call("GetAllContentControls")
            controlLength = contentControls.GetLength()
            print(controlLength)
            for j in range(controlLength):
                print(contentControls.Get(j).Call("GetElement", 0).Call("GetText").ToString())
                print(contentControls.Get(j).Call("GetClassType").ToString())
                print(contentControls.Get(j).Call("GetTag").ToString())
                print(paragraph.Call("GetText").ToString())

    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:
        builder.CloseFile()
   
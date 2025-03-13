import os
import docbuilder


builder = docbuilder.CDocBuilder()
file_path = os.path.join(os.getcwd(), "lang", "source","office_vacation", "Федорова_Ольга.pdf")
file_path = os.path.join(os.getcwd(), "lang", "source", "office_vacation","Романова_Екатерина.pdf")
#file_path = os.path.join(os.getcwd(), "lang", "source","office_vacation", "Иванов_Иван.pdf")

if not os.path.exists(file_path):
    raise FileNotFoundError(f"Файл '{file_path}' не найден.")

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
    text = []
    for i in range(length):
        text.append(document.Call("GetElement", i).Call("GetText").ToString())

except Exception as e:
    print(f"Произошла ошибка: {e}")
finally:
    builder.CloseFile()
   
print(text)


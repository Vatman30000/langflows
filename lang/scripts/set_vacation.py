import os
import docbuilder
# Список ФИО
names = [
    'Иванов Иван Иванович',
    'Петров Петр Петрович',
    'Сидоров Алексей Алексеевич',
    'Кузнецова Мария Сергеевна',
    'Орлов Дмитрий Викторович',
    'Зайцева Анна Павловна',
    'Васильев Евгений Олегович',
    'Федорова Ольга Николаевна',
    'Романова Екатерина Михайловна',
    'Леонов Артем Андреевич'
]

# Даты начала отпуска
start_dates = [
    '01-07-2023', '05-08-2023', '15-09-2023', '25-10-2023', '03-11-2023',
    '12-12-2023', '22-01-2024', '02-02-2024', '13-03-2024', '24-04-2024'
]

# Даты окончания отпуска
end_dates = [
    '10-07-2023', '14-08-2023', '24-09-2023', '04-11-2023', '12-11-2023',
    '19-12-2023', '29-01-2024', '09-02-2024', '20-03-2024', '01-05-2024'
]
builder = docbuilder.CDocBuilder()
for i in range(len(names)):
    file_type = "docx"
    

    builder.CreateFile(f"{file_type}")
    context = builder.GetContext()
    scope = context.CreateScope()

    globalObj = context.GetGlobal()

    api = globalObj["Api"]
    document = api.Call("GetDocument")
    paragraph = api.Call("CreateParagraph")
    paragraph.Call("SetSpacingAfter", 1000, False)
    paragraph.Call("AddText", "От:")
    content = context.CreateArray(1)
    content[0] = paragraph
    document.Call("InsertContent", content)

    inlineLvlSdt = api.Call("CreateInlineLvlSdt")
    paragraph.Call("AddInlineLvlSdt", inlineLvlSdt)
    run = api.Call("CreateRun")
    run.Call("AddText", names[i] )
    inlineLvlSdt.Call("AddElement",run,0)
    paragraph.Call("Push", inlineLvlSdt)
    inlineLvlSdt.Call("SetTag", "person")


    paragraph = api.Call("CreateParagraph")
    paragraph.Call("SetSpacingAfter", 1000, False)
    paragraph.Call("AddText", "Прошу предоставить мне ежегодный оплачиваемый отпуск на период ")
    content = context.CreateArray(1)
    content[0] = paragraph
    document.Call("InsertContent", content)

    inlineLvlSdt = api.Call("CreateInlineLvlSdt")
    paragraph.Call("AddInlineLvlSdt", inlineLvlSdt)
    run = api.Call("CreateRun")
    run.Call("AddText", start_dates[i])
    inlineLvlSdt.Call("AddElement",run,0)
    paragraph.Call("Push", inlineLvlSdt)
    inlineLvlSdt.Call("SetTag", "start_date")

    paragraph.Call("AddText", " по ")
    content = context.CreateArray(1)
    content[0] = paragraph
    document.Call("InsertContent", content)

    inlineLvlSdt = api.Call("CreateInlineLvlSdt")
    paragraph.Call("AddInlineLvlSdt", inlineLvlSdt)
    run = api.Call("CreateRun")
    run.Call("AddText", end_dates[i])
    inlineLvlSdt.Call("AddElement",run,0)
    paragraph.Call("Push", inlineLvlSdt)
    inlineLvlSdt.Call("SetTag", "end_date")

    dstPath = os.path.join(os.getcwd(), 
             "lang", 
             "source", 
             "office_vacation",
             f"{'_'.join(names[i].split()[:2])}.{file_type}"
            )

    builder.SaveFile(file_type, dstPath)
    builder.CloseFile()

import os

def get_file_paths(folder_path):
    file_paths = []
    
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".pdf") or file.endswith(".docx"):
                file_path = os.path.join(root, file)
                file_paths.append(file_path)
                
    return file_paths

folder_path = r"/home/alexandr/Yandex.Disk/pyprojects/langflow/lang/source/office_vacation"  # Укажите путь к вашей папке
file_paths = get_file_paths(folder_path)

for path in file_paths:
    print(path)

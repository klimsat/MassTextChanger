import pandas as pd
import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox, Scrollbar
import pyperclip

# Функция для выбора папки
def select_folder():
    folder_path = filedialog.askdirectory()
    path_text.delete(0, tk.END)  # Удаляем старый путь
    path_text.insert(0, folder_path)  # Вставляем новый путь

# Функция для замены слов
def replace_words():
    # Получаем путь к папке из поля ввода
    folder_path = path_text.get()

    # Получаем данные из полей ввода
    old_words = old_text.get("1.0", tk.END).splitlines()
    new_words = new_text.get("1.0", tk.END).splitlines()

    # Получаем список расширений из поля ввода
    extensions = [ext.strip() for ext in ext_text.get().split(',')]

    # Проверяем, что количество строк в обоих полях совпадает
    if len(old_words) != len(new_words):
        messagebox.showerror("Ошибка", "Количество строк в обоих полях различаются, исправьте это и попробуйте повторить запуск замены текста.")
        return

    # Создаем DataFrame из полученных данных
    df = pd.DataFrame({
        'old': old_words,
        'new': new_words
    })

    # Проверяем состояние чекбоксов
    whole_words_only = whole_var.get()
    case_sensitive = case_var.get()

    # Счетчик для подсчета количества замен
    count = 0

    # Проходим по всем файлам в указанной папке и ее подпапках
    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            # Проверяем, что расширение файла есть в списке
            if any(filename.endswith('.' + ext) for ext in extensions):
                file_path = os.path.join(root, filename)
                with open(file_path, 'r', encoding='utf-8') as file:
                    file_data = file.read()
                
                # Проходим по каждой паре замен в DataFrame
                for index, row in df.iterrows():
                    # Заменяем старые слова на новые
                    old_word = row['old']
                    new_word = row['new']
                    if whole_words_only:
                        old_word = r'\b' + old_word + r'\b'
                    flags = 0 if case_sensitive else re.IGNORECASE
                    file_data, num = re.subn(old_word, new_word, file_data, flags=flags)
                    count += num
                
                # Записываем обновленные данные обратно в файл
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(file_data)

    # Показываем сообщение с количеством замен
    messagebox.showinfo("Замены завершены", f"Было сделано {count} замен.")

# Функция для копирования текста
def copy(event:tk.Event=None) -> str:
    try:
        text = event.widget.selection_get()
        pyperclip.copy(text)
    except tk.TclError:
        pass
    return "break"

# Функция для выделения всего текста
def select_all(event:tk.Event=None) -> str:
    event.widget.tag_add(tk.SEL, "1.0", tk.END)
    return "break"

# Функция для обработки событий клавиатуры
def callback(event):
    ctrl = (event.state & 0x4) != 0
    if event.keycode==86 and ctrl and event.keysym.lower() != "v":
        event.widget.event_generate("<<Paste>>")
    if event.keycode==67 and ctrl and event.keysym.lower() != "c":
        event.widget.event_generate("<<Copy>>")
    if event.keycode==65 and ctrl and event.keysym.lower() != "a":
        event.widget.event_generate("<<SelectAll>>")

# Создаем окно tkinter
root = tk.Tk()
root.title("Программа для массовой замены слов в файлах")
root.bind("<Key>", callback)

# Создаем поля ввода для старых и новых слов
text_frame = tk.Frame(root)
text_frame.pack(side=tk.LEFT)

old_frame = tk.Frame(text_frame)
old_frame.pack(side=tk.LEFT)
tk.Label(old_frame, text="Найти:").pack()
old_text = tk.Text(old_frame, height=10, width=30, wrap="none")
old_text.pack(fill=tk.Y)
old_text.bind("<Control-c>", copy)
old_text.bind("<Control-a>", select_all)

# Добавляем горизонтальную полосу прокрутки для old_text
xscrollbar_old = Scrollbar(old_frame, orient='horizontal', command=old_text.xview)
xscrollbar_old.pack(side=tk.BOTTOM, fill=tk.X)
old_text['xscrollcommand'] = xscrollbar_old.set

new_frame = tk.Frame(text_frame)
new_frame.pack(side=tk.LEFT)
tk.Label(new_frame, text="Заменить на:").pack()
new_text = tk.Text(new_frame, height=10, width=30, wrap="none")
new_text.pack(fill=tk.Y)
new_text.bind("<Control-c>", copy)
new_text.bind("<Control-a>", select_all)

# Добавляем горизонтальную полосу прокрутки для new_text
xscrollbar_new = Scrollbar(new_frame, orient='horizontal', command=new_text.xview)
xscrollbar_new.pack(side=tk.BOTTOM, fill=tk.X)
new_text['xscrollcommand'] = xscrollbar_new.set

# Добавляем вертикальную полосу прокрутки для обоих текстовых полей
yscrollbar = Scrollbar(text_frame, command=lambda y: (old_text.yview(y), new_text.yview(y)))
yscrollbar.pack(side=tk.RIGHT, fill=tk.Y)
old_text['yscrollcommand'] = yscrollbar.set
new_text['yscrollcommand'] = yscrollbar.set

# Создаем чекбоксы для опций "Только целые слова" и "Учитывать регистр"
whole_var = tk.IntVar(value=1)
case_var = tk.IntVar(value=1)
whole_check = tk.Checkbutton(root, text="Только целые слова", variable=whole_var, anchor='w')
whole_check.pack(fill=tk.X, padx=30)
case_check = tk.Checkbutton(root, text="Учитывать регистр", variable=case_var, anchor='w')
case_check.pack(fill=tk.X, padx=30)

# Создаем поле ввода для расширений файлов
ext_frame = tk.Frame(root)
ext_frame.pack(fill=tk.X, padx=30)
tk.Label(ext_frame, text="Фильтры:", width=10, anchor='w').pack(side=tk.LEFT)
ext_text = tk.Entry(ext_frame, width=30)
ext_text.insert(0, "yml,txt")  # Значение по умолчанию
ext_text.pack(side=tk.LEFT, fill=tk.X)

# Создаем поле ввода для пути к папке и кнопку выбора папки
path_frame = tk.Frame(root)
path_frame.pack(fill=tk.X, padx=30)
tk.Label(path_frame, text="Путь к папке:", width=10, anchor='w').pack(side=tk.LEFT)
path_text = tk.Entry(path_frame, width=30)
path_text.pack(side=tk.LEFT, fill=tk.X)
select_button = tk.Button(path_frame, text="...", command=select_folder)
select_button.pack(side=tk.LEFT)

# Создаем кнопку, которая вызывает функцию replace_words при нажатии
replace_button = tk.Button(root, text="Сделать замены", command=replace_words)
replace_button.pack(pady=20)

# Запускаем цикл событий tkinter
root.mainloop()

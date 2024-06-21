import tkinter as tk
from tkinter import messagebox
import configparser # создание конфига
import data_csv.lib_data_csv as lib_data_csv

class CustomConfig:
    def __init__(self):
        self.filePath = None
        self.statusCheckBox = None
        self.comboboxes = []
        self.entries = []

    def create(self, classArr, root):
        # создаём объект конфигурации
        config = configparser.ConfigParser()
        # Читаем файл конфигурации, если он существует
        config.read('config.cfg')
        config.clear()
        for item in classArr:
            # Проверка существования раздела
            if item.tabTitle not in config:
                # Если раздела нет - создать
                config[item.tabTitle] = {}
            try:
                self.get_gui_data(item)
            except Exception:
                messagebox.showerror('Ошибка', 'get_gui_data')
            try:
                self.save_cfg(config, item)
            except Exception:
                messagebox.showerror('Ошибка', 'save_cfg')
            self.comboboxes = []
            self.entries = []
            self.statusCheckBox = None
            self.filePath = None
            self.historyPath = []
            # Закрытие окна
        root.destroy()

    def get_gui_data(self, className):
        # Путь до файла
        if hasattr(className, "path"):
        #if className.path != None:
            self.filePath = className.path
        else: self.filePath = ''
        # История путей до файла
        if hasattr(className, "oldPath"):
            self.historyPath = className.oldPath
        else:
            self.historyPath = []
        # Статус checkBox
        if hasattr(className, "checkButton"):
            self.statusCheckBox = str(className.var.get())
        # оси
        for item in className.comboboxes:
            self.comboboxes.append(item.get())
        # количество ячеек
        for item in className.entries:
            self.entries.append(item.get())

    def save_cfg(self, config, className):
        counter = 0
        if self.filePath != None:
            config[f'{className.tabTitle}']['File Path'] = self.filePath

        for item in range(0, len(self.historyPath)):
            counter += 1
            config[f'{className.tabTitle}'][f'History Path {counter}'] = self.historyPath[item]

        if counter == 0:
            config[f'{className.tabTitle}'][f'History Path {1}'] = ''
        counter = 0

        if self.statusCheckBox!= None:
            config[f'{className.tabTitle}']['Status checkbox'] = self.statusCheckBox
        for item in range(0, len(self.comboboxes)):
            counter+=1
            self.comboboxes[item] = self.comboboxes[item].replace('%','%%')
            config[f'{className.tabTitle}'][f'Combobox {counter}'] = self.comboboxes[item]
        counter = 0
        for item in range(0, len(self.entries)):
            counter+=1
            config[f'{className.tabTitle}'][f'Entry {counter}'] = self.entries[item]
        with open('config.cfg', 'w', encoding='utf-8') as configfile:
            config.write(configfile)

    def get_cfg_data(self, className):
        config = configparser.ConfigParser()
        config.read('config.cfg', encoding='utf-8')
    
        counter = 0
        if f'{className.tabTitle}' in config:
            className.path = config[f'{className.tabTitle}'].get('File Path')

            counter = 1
            while (config[f'{className.tabTitle}'].get(f'History Path {counter}')):
                if (config[f'{className.tabTitle}'].get(f'History Path {counter}')) != '':
                    className.oldPath.append(config[f'{className.tabTitle}'].get(f'History Path {counter}'))
                counter += 1
            counter = 0

            if hasattr(className, "selectedFileLabel"):
                className.selectedFileLabel.config(text='Последний выбранный файл: ' + className.path)
            if hasattr(className, "checkButton"):
                className.var.set(int(config[f'{className.tabTitle}'].get('Status checkbox')))
            for item in className.comboboxes:
                counter+=1
                item.set(config[f'{className.tabTitle}'].get(f'Combobox {counter}'))
                if className.path != '':
                    strArr = lib_data_csv.file_read_lines(className.path)
                    if strArr == 0:
                        return
                    dataArr = strArr[0].split(";")  # Добавили только заголовки
                    className.update_axis_combobox(dataArr, item)
            counter = 0
            for item in className.entries:
                counter+=1
                item.insert(tk.END, config[f'{className.tabTitle}'].get(f'Entry {counter}'))
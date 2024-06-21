############################### Libraries ######################################
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import re # работа с регулярными выражениями
import ast #Корректность формулы
import surface.app_surface_gen as app_surface_gen
import approximation.app_approximation as app_approximation
import vector.app_vector as app_vector
import common.lib_common as lib_common
import data_csv.lib_data_csv as lib_data_csv
import config.config_creating as cfg

############################### Classes ######################################
class CommonFunc:
    def __init__(self):
        self.path = '' #Текущий путь до файла
        #self.oldPath = [] #Прошлые пути до файла

    def select_input_file(self, labelObj, className):
        filePath = filedialog.askopenfilename(filetypes=(("CSV files", "*.csv"), ("All files", "*.*")))
        if filePath:
            labelObj.config(text='Последний выбранный файл: ' + filePath)
            strArr = lib_data_csv.file_read_lines(filePath)
            dataArr = strArr[0].split(";")  # Добавили только заголовки
            for item in className.comboboxes:
                self.update_axis_combobox(dataArr, item)
            self.path = filePath  # сохраняем путь до файла в глобальной переменной

    def update_axis_combobox(self, values, obj = None):
        if obj != None:
            obj['values'] = values

    def reset_data(self, className, labelObj=None):
        self.path=''
        #Очищаем все Combobox
        for item in className.comboboxes:
            self.update_axis_combobox('', item)
            item.set('')
        # Очищаем все Entry
        for item in className.entries:
            item.delete(0, tk.END)
        for item in className.variables:
            item = []
        if labelObj != None:
            labelObj.config(text='Последний выбранный файл: ')

    def insert_variable(event, listObj, entryObj): #event
        selectedVar = listObj.get(listObj.curselection())
        #Считываем позицию курсора
        position = entryObj.index(tk.INSERT)
        textBeforeCursor = entryObj.get()[:position] # Получаем текст до индекса курсора
        parts = re.split(r'[-+*/(]', textBeforeCursor) # Разделяем текст на части по знакам "+", "-", "*", "/"
        lastPart = parts[-1] # Получаем последнюю часть (то, что находится левее курсора)
        entryObj.delete(position - len(lastPart), position) # Удаляем найденную часть из поля ввода
        entryObj.insert(position, selectedVar)  # добавляет текст из variable на место курсора
        listObj.pack_forget()  # Скрывает List с экрана
        entryObj.focus_set()  # устанавливает фокус на Entry, чтобы после выбора из списка не нужно было снова тыкать на Entry

    def show_variable_list(event, path, entryObj, listObj): # event
        formula = entryObj.get()
        cursor_position = entryObj.index(tk.INSERT)
        parts = lib_common.re.split(r'[+\-*/( ]', formula[:cursor_position])
        currentPart = parts[-1] if parts else ''
        listObj.delete(0, tk.END)
        resultArr = []
        if path:
            strArr = lib_data_csv.file_read_lines(path)
            dataArr = strArr[0].split(";")  # Добавили только заголовки
            tempArr = strArr[1].split(";") #Временный массив для доп. проверки
            for iter in range(len(dataArr)):
                if lib_common.re.match("^[0-9,]+$", tempArr[iter]):
                    if lib_common.re.search(r'^\S+,', dataArr[iter]):
                        resultArr.append(dataArr[iter].split(",")[0])
                    else:
                        resultArr.append(dataArr[iter].split(" ")[0])
        else:
            resultArr = []
        matchingVars = [var for var in resultArr if var.startswith(currentPart)]
        if len(matchingVars) > 0:
            if matchingVars[0] != '':
                for var in matchingVars:
                    listObj.insert(tk.END, var)
                if matchingVars:
                    #listObj.place(relx=0.5, y=305, anchor="n")
                    pass
                else:
                    listObj.pack_forget()

    def copy_to_clipboard(self, copyObj):
        if isinstance(copyObj, str):
            lib_data_csv.pyperclip.copy(copyObj)
        else:
            strBuf = lib_data_csv.generate_csv_buf(copyObj)  # записываем в csv файл
            lib_data_csv.pyperclip.copy(strBuf)

    def download_file(self, downloadObj):
        strBuf = lib_data_csv.generate_csv_file(downloadObj)  # записываем в csv файл
        filePath = filedialog.asksaveasfilename(defaultextension=".csv")
        with open(filePath, mode="w") as file:
            file.write(strBuf)

class Surface(ttk.Frame, CommonFunc):
    # Список созданных элементов
    comboboxes, entries, variables = [], [], []
    def __init__(self, parent, tabTitle):
        super().__init__(parent)
        super().__init__()
        self.tabTitle = tabTitle
        self._allDataFromFile = []
        Surface.variables.append(self._allDataFromFile)
        self.csvRecordList = ''
        #self.var = app_vector.IntVar()
        self.var = tk.IntVar()
        self.checkButton = tk.Checkbutton(self, text="Сбрасывать данные при запуске программы", variable=self.var, onvalue=1, offvalue=0)
        self.checkButton.place(relx=0.5, y=20, anchor="n")
        self.checkButton.select() # активное исходное состояние
        self.oldPath = []

        # Надпись после выбора файла
        self.selectedFileLabel = ttk.Label(self, text='Последний выбранный файл: ')
        self.selectedFileLabel.pack()

        # Раздел выбора файла во вкладке "Создание поверхности"
        fileFrame = ttk.LabelFrame(self, text="Выберите CSV-файл")
        fileFrame.place(relx=0.5, y=50, anchor="n")

        fileButton = ttk.Button(fileFrame, text="Выбрать файл", command=lambda:self.select_input_file(labelObj=self.selectedFileLabel, className=Surface))
        fileButton.config(width=25)
        fileButton.pack(padx = 10, pady = 5)

        resetButton = ttk.Button(self, text="Сбросить файлы", command=self.reset_data_file)
        resetButton.place(relx=0.25, y=120, anchor="n")
        resetButton.config(width=25)

        resetSettingsButton = ttk.Button(self, text="Сбросить настройки", command=lambda:self.reset_data(Surface, self.selectedFileLabel))
        resetSettingsButton.place(relx=0.75, y=120, anchor="n")
        resetSettingsButton.config(width=25)

        # Раздел выбора осей, ввода параметров и кнопки запуска программы во вкладке "Создание поверхности"
        xAxisLabel = ttk.Label(self, text="Выберите базовую ось X:")
        xAxisLabel.place(relx=0.5, y=150, anchor="n")

        xAxisValues=[]
        self.xAxisCombobox = ttk.Combobox(self,values=xAxisValues, state='readonly')
        self.xAxisCombobox.place(relx=0.5, y=180, anchor="n")
        self.xAxisCombobox.config(width=40)
        Surface.comboboxes.append(self.xAxisCombobox)

        yAxisLabel = ttk.Label(self, text="Выберите базовую ось Y:")
        yAxisLabel.place(relx=0.5, y=210, anchor="n")

        self.yAxisValues=[]
        self.yAxisCombobox = ttk.Combobox(self, values=self.yAxisValues, state='readonly')
        self.yAxisCombobox.place(relx=0.5, y=240, anchor="n")
        self.yAxisCombobox.config(width=40)
        Surface.comboboxes.append(self.yAxisCombobox)

        #Список для отображения переменных
        variableList = tk.Listbox(self)
        variableList.bind("<Double-Button-1>", lambda _:self.insert_variable(listObj=variableList, entryObj=self.formulaEntry))
        variableList.place(relx=0.5, y=450, anchor="n")

        formulaLabel = ttk.Label(self, text="Введите формулу.")
        formulaLabel.place(relx=0.5, y=390, anchor="n")

        zLabel = ttk.Label(self, text="Z=")
        zLabel.place(relx=0.08, y=420)

        self.formulaEntry = ttk.Entry(self)
        self.formulaEntry.place(relx=0.5, y=420, anchor="n")
        self.formulaEntry.config(width=40)
        #<KeyRelease> - отпускание клавиши
        self.formulaEntry.bind("<KeyRelease>", lambda _: self.show_variable_list(path=self.path, entryObj=self.formulaEntry, listObj=variableList))
        # <ButtonRelease-1> - отпускание ЛКМ
        self.formulaEntry.bind("<ButtonRelease-1>",
                               lambda _: self.show_variable_list(path=self.path, entryObj=self.formulaEntry,
                                                                 listObj=variableList))
        #"<FocusIn>" - фокус на виджете
        self.formulaEntry.bind("<FocusIn>", lambda _: self.show_variable_list(path=self.path, entryObj=self.formulaEntry, listObj=variableList))
        Surface.entries.append(self.formulaEntry)

        zMinLabel = ttk.Label(self, text="Z_min=")
        zMinLabel.place(relx=0.08, y=450)

        self.zMinEntry = ttk.Entry(self)
        self.zMinEntry.place(relx=0.25, y=450, anchor="n")
        self.zMinEntry.config(width=5)
        Surface.entries.append(self.zMinEntry)

        zMaxLabel = ttk.Label(self, text="Z_max=")
        zMaxLabel.place(relx=0.08, y=480)

        self.zMaxEntry = ttk.Entry(self)
        self.zMaxEntry.place(relx=0.25, y=480, anchor="n")
        self.zMaxEntry.config(width=5)
        Surface.entries.append(self.zMaxEntry)

        runButton = ttk.Button(self, text="Запустить программу", command=self.run)
        runButton.place(relx=0.5, y=630, anchor="n")
        runButton.config(width=25)

        copyButton = ttk.Button(self, text="Скопировать результат", command=lambda:self.copy_to_clipboard(self.csvRecordList))
        copyButton.place(relx=0.5, y=660, anchor="n")
        copyButton.config(width=25)

        downloadButton = ttk.Button(self, text="Скачать таблицу", command=lambda: self.download_file(self.csvRecordList))
        downloadButton.place(relx=0.5, y=690, anchor="n")
        downloadButton.config(width=25)

        xAxisVector = ttk.Label(self, text="Введите вектор Х:")
        xAxisVector.place(relx=0.5, y=270, anchor="n")

        self.xAxisVector = ttk.Entry(self)
        self.xAxisVector.place(relx=0.5, y=300, anchor="n")
        self.xAxisVector.config(width=40)
        Surface.entries.append(self.xAxisVector)

        yAxisVector = ttk.Label(self, text="Введите вектор Y:")
        yAxisVector.place(relx=0.5, y=330, anchor="n")

        self.yAxisVector = ttk.Entry(self)
        self.yAxisVector.place(relx=0.5, y=360, anchor="n")
        self.yAxisVector.config(width=40)
        Surface.entries.append(self.yAxisVector)

    def reset_data_file(self):
        self._allDataFromFile = []
        self.oldPath = []
        self.selectedFileLabel.config(text='Последний выбранный файл: ')
        for item in Surface.comboboxes:
            self.update_axis_combobox('', item)

    def run(self):
        # ПРОВЕРКИ
        xAxis = self.xAxisCombobox.get()
        if len(xAxis) == 0:
            messagebox.showerror('Ошибка', 'Не задана ось Х.')
            return
        yAxis = self.yAxisCombobox.get()
        if len(yAxis) == 0:
            messagebox.showerror('Ошибка', 'Не задана ось Y.')
            return

        if not self.xAxisVector.get():
            messagebox.showerror('Ошибка', 'Неверное задан вектор Х.')
            return

        if not self.yAxisVector.get():
            messagebox.showerror('Ошибка', 'Неверное задан вектор Y.')
            return

        formula = self.formulaEntry.get()
        try:
            ast.parse(formula)
        except SyntaxError:
            messagebox.showerror('Ошибка', 'Формула не корректна.')
            return

        zMin = self.zMinEntry.get()
        if zMin:
            try:
                # Проверяем, что введенное значение может быть преобразовано в число
                zMin = float(zMin)
            except ValueError:
                messagebox.showerror('Ошибка', 'Ввод некорректен (z_min). Введите число.')
                return

        zMax = self.zMaxEntry.get()
        if zMax:
            try:
                # Проверяем, что введенное значение может быть преобразовано в число
                zMax = float(zMax)
            except ValueError:
                messagebox.showerror('Ошибка', 'Ввод некорректен (z_max). Введите число.')
                return
        if zMax and zMin:
            if zMax <= zMin:
                messagebox.showerror('Ошибка', 'z_max не может быть меньше z_min.')
                return

        xAxisVector = self.xAxisVector.get()
        xAxisVector = xAxisVector.replace(',','.')
        xAxisVector = re.findall(r'-?\b\d+(?:\.\d+)?\b', xAxisVector)
        if len(xAxisVector) < 3:
            messagebox.showerror('Ошибка', 'Вектор X должен содержать минимум 3 значения.')
            return

        yAxisVector = self.yAxisVector.get()
        yAxisVector = yAxisVector.replace(',', '.')
        yAxisVector = re.findall(r'-?\b\d+(?:\.\d+)?\b', yAxisVector)
        if len(yAxisVector) < 3:
            messagebox.showerror('Ошибка', 'Вектор Y должен содержать минимум 3 значения.')
            return

        # ПРОГРАММА
        if self.var.get() == 1:
            dataFromFile = lib_data_csv.file_read_lines(self.path)
            if dataFromFile == 0:
                return 0
            strArr = dataFromFile[0].split(";")  # Добавили только заголовки
            for iter in range(0, len(strArr)):
                if (xAxis == strArr[iter]) or (xAxis == strArr[iter][:-1]):
                    columnX = iter
                if (yAxis == strArr[iter]) or (yAxis == strArr[iter][:-1]):
                    columnY = iter
            tempArr = strArr  # Добавили только заголовки
            for iter in range(1, len(strArr)):
                tempArr[iter] = strArr[iter].split(",")[0] #Разделяем заголовок по "," и присваиваем часть до ","
                tempArr[iter] = strArr[iter].split(" ")[0] #Разделяем заголовок по " " и присваиваем часть до " "
            self._allDataFromFile = lib_common.data_arr_creating(dataFromFile)
            arrZ = app_surface_gen.columnZ_creating(self._allDataFromFile, formula, tempArr)
            pointsArr = app_surface_gen.points_arr_creating(self._allDataFromFile, columnX, columnY, arrZ)

            sortedPoints = app_surface_gen.points_sort(xAxisVector, yAxisVector, pointsArr)
            nodePoints = app_surface_gen.node_points(xAxisVector, yAxisVector, sortedPoints, zMin, zMax)
            if nodePoints == -1:
                messagebox.showerror('Ошибка', 'Хотя бы одна точка должна быть на поверхности.')
                return
            csvRecord = app_surface_gen.replace_symbols_surface(nodePoints, '.', ',')
            self.csvRecordList = app_surface_gen.process_list_to_csvFormat_surface(csvRecord)
            csvRecord = app_surface_gen.replace_symbols_surface(nodePoints, ',', '.')
            app_surface_gen.surface(nodePoints, pointsArr, xAxisVector, yAxisVector, zMin, zMax)
            self._allDataFromFile = []
            self.oldPath = []
        else:
            dataFromFile = lib_data_csv.file_read_lines(self.path)
            strArr = dataFromFile[0].split(";")  # Добавили только заголовки
            for iter in range(0, len(strArr)):
                if (xAxis == strArr[iter]) or (xAxis == strArr[iter][:-1]):
                    columnX = iter
                if (yAxis == strArr[iter]) or (yAxis == strArr[iter][:-1]):
                    columnY = iter
            tempArr = strArr  # Добавили только заголовки
            for iter in range(1, len(strArr)):
                tempArr[iter] = strArr[iter].split(",")[0]  # Разделяем заголовок по "," и присваиваем часть до ","
                tempArr[iter] = strArr[iter].split(" ")[0]  # Разделяем заголовок по " " и присваиваем часть до " "
            dataArr = lib_common.data_arr_creating(dataFromFile)

            for path in self.oldPath:
                data = lib_data_csv.file_read_lines(path)
                data = lib_common.data_arr_creating(data)
                self._allDataFromFile = self._allDataFromFile + data

            check = False
            for path in self.oldPath:
                if self.path == path:
                    check = True
            if check==False:
                self._allDataFromFile = self._allDataFromFile + dataArr

            arrZ = app_surface_gen.columnZ_creating(self._allDataFromFile, formula, tempArr)
            pointsArr = app_surface_gen.points_arr_creating(self._allDataFromFile, columnX, columnY, arrZ)
            sortedPoints = app_surface_gen.points_sort(xAxisVector, yAxisVector, pointsArr)
            # Проверка на то, попадают ли точки в вектор
            counter = 0
            for iter in range(len(sortedPoints)):
                for jter in range(len(sortedPoints[iter])):
                    if len(sortedPoints[iter][jter]) != 0:
                        counter = 1
            if counter == 0:
                messagebox.showerror('Ошибка', 'Хотя бы одна точка должна входить в заданный вектор.')
                return
            nodePoints = app_surface_gen.node_points(xAxisVector, yAxisVector, sortedPoints, zMin, zMax)
            csvRecord = app_surface_gen.replace_symbols_surface(nodePoints, '.', ',')
            self.csvRecordList = app_surface_gen.process_list_to_csvFormat_surface(csvRecord)
            csvRecord = app_surface_gen.replace_symbols_surface(nodePoints, ',', '.')
            app_surface_gen.surface(nodePoints, pointsArr, xAxisVector, yAxisVector, zMin, zMax)
            check = False
            for path in self.oldPath:
                if path == self.path:  # Если такой файл ещё не был открыт
                    check = True  # Такой файл уже открывался
            if check == False:
                self.oldPath.append(self.path)
            self._allDataFromFile = []

class Approximation(ttk.Frame, CommonFunc):
    # Список созданных элементов
    comboboxes, entries, variables = [], [], []

    def __init__(self, parent, tabTitle):
        super().__init__(parent)
        super().__init__()
        self.tabTitle = tabTitle
        self.csvRecordList, self.formula = '', ''

        # Надпись после выбора файла
        self.selectedFileLabel = ttk.Label(self, text='Выбранный файл: ')
        self.selectedFileLabel.pack()

        # Раздел выбора файла во вкладке "Аппроксимация"
        fileFrame = ttk.LabelFrame(self, text="Выберите CSV-файл")
        fileFrame.place(relx=0.5, y=20, anchor="n")

        fileButton = ttk.Button(fileFrame, text="Выбрать файл", command=lambda :self.select_input_file(self.selectedFileLabel, Approximation))
        fileButton.config(width=25)
        fileButton.pack(padx=10, pady=10)

        resetSettingsButton = ttk.Button(self, text="Сбросить настройки", command=lambda :self.reset_data(Approximation, self.selectedFileLabel))
        resetSettingsButton.place(relx=0.5, y=90, anchor="n")
        resetSettingsButton.config(width=25)

        # Раздел выбора осей, ввода параметров и кнопки запуска программы во вкладке "Аппроксимация"
        xAxisLabel = ttk.Label(self, text="Выберите данные УОЗ:")
        xAxisLabel.place(relx=0.5, y=120, anchor="n")

        xAxisValues=[]
        self.xAxisCombobox = ttk.Combobox(self, values=xAxisValues, state='readonly')
        self.xAxisCombobox.place(relx=0.5, y=150, anchor="n")
        self.xAxisCombobox.config(width=40)
        Approximation.comboboxes.append(self.xAxisCombobox)

        yAxisValues=[]
        yAxisLabel = ttk.Label(self, text="Выберите данные крутящего момента:")
        yAxisLabel.place(relx=0.5, y=180, anchor="n")

        self.yAxisCombobox = ttk.Combobox(self, values=yAxisValues, state='readonly')
        self.yAxisCombobox.place(relx=0.5, y=210, anchor="n")
        self.yAxisCombobox.config(width=40)
        Approximation.comboboxes.append(self.yAxisCombobox)

        step = ttk.Label(self, text="Шаг:")
        step.place(relx=0.5, y=240, anchor="n")

        self.stepEntry = ttk.Entry(self)
        self.stepEntry.place(relx=0.5, y=270, anchor="n")
        self.stepEntry.config(width=40)
        Approximation.entries.append(self.stepEntry)

        formulaLabel = ttk.Label(self, text="Полученная формула:")
        formulaLabel.place(relx=0.5, y=300, anchor="n")

        self.formulaEntry = ttk.Entry(self)
        self.formulaEntry.place(relx=0.5, y=330, anchor="n")
        self.formulaEntry.config(width=40)
        Approximation.entries.append(self.formulaEntry)

        runButton = ttk.Button(self, text="Запустить программу", command=self.run)
        runButton.config(width=25)
        runButton.place(relx=0.5, y=360, anchor="n")

        copyButton = ttk.Button(self, text="Скопировать результат", command=lambda :self.copy_to_clipboard(self.formula))
        copyButton.config(width=25)
        copyButton.place(relx=0.5, y=390, anchor="n")

        downloadButton = ttk.Button(self, text="Скачать таблицу", command=lambda :self.download_file(self.csvRecordList))
        downloadButton.config(width=25)
        downloadButton.place(relx=0.5, y=420, anchor="n")

    def run(self):
        # ПРОВЕРКИ
        xAxis = self.xAxisCombobox.get()
        if len(xAxis) == 0:
            messagebox.showerror('Ошибка', 'Не задан УОЗ.')
            return
        yAxis = self.yAxisCombobox.get()
        if len(yAxis) == 0:
            messagebox.showerror('Ошибка', 'Не задан крутящий момент.')
            return
        step = self.stepEntry.get()
        if not self.is_float(step) or float(step) < 0:
            messagebox.showerror('Ошибка', 'Неверное задан шаг.')
            return

        headings = lib_data_csv.file_read_lines(self.path)[0]  # наименования столбцов
        strArr = headings
        strArr = strArr.split(";")  # Добавили только заголовки
        referenceCol_1 = 0  # номер столбца УОЗ
        referenceCol_2 = 0  # номер столбца рутящего момента
        counter = 0  # счётчик
        for name in strArr:
            if (xAxis == name) or (xAxis == name[:-1]):
                referenceCol_1 = counter
            if (yAxis == name) or (yAxis ==name[:-1]):
                referenceCol_2 = counter
            counter += 1
        # преобразовываем csv файл в массив, с которым работаем
        dataArr = lib_data_csv.process_csv_file(self.path)
        # очищаем лишние данные
        resultArr = app_approximation.process_list(dataArr, referenceCol_1, step)
        csvRecord = lib_common.replace_symbols(resultArr, '.', ',')
        # преобразовываем список в тот вид, который подходит для записи в csv файл
        csvRecord = lib_data_csv.process_list_to_csvFormat(csvRecord)
        csvRecord.insert(0, headings)  # вставляем в начало наименования столбцов
        self.csvRecordList = csvRecord
        resultArr = lib_common.replace_symbols(resultArr, ',', '.')
        # аппроксимация и построение графика; 3 - степень аппроксимации
        self.formula = app_approximation.approx_func(resultArr, 2, referenceCol_1, referenceCol_2, strArr[referenceCol_1], strArr[referenceCol_2])
        self.update_entry(self.formulaEntry, self.formula)

    def is_float(self, str):
        try:
            float(str)
            return True
        except ValueError:
            return False

    def update_entry(self, entryObj, formula):
        entryObj.delete(0, tk.END)
        entryObj.insert(0, formula)

class Vector(ttk.Frame, CommonFunc):
    # Список созданных элементов
    comboboxes, entries, variables = [], [], []
    def __init__(self, parent, tabTitle):
        super().__init__(parent)
        super().__init__()
        self.tabTitle = tabTitle
        self.csvRecordList = ''
        # Надпись после выбора файла
        self.selectedFileLabel = ttk.Label(self, text='Выбранный файл: ')
        self.selectedFileLabel.pack()

        # Раздел выбора файла во вкладке "Создание вектора"
        fileFrame = ttk.LabelFrame(self, text="Выберите CSV-файл")
        fileFrame.place(relx=0.5, y=20, anchor="n")

        fileButton = ttk.Button(fileFrame, text="Выбрать файл", command=lambda :self.select_input_file(self.selectedFileLabel, Vector))
        fileButton.pack(padx=10, pady=5)
        fileButton.config(width=25)

        resetSettingsButton = ttk.Button(self, text="Сбросить настройки", command=lambda :self.reset_data(Vector, self.selectedFileLabel))
        resetSettingsButton.place(relx=0.5, y=90, anchor="n")
        resetSettingsButton.config(width=25)

        # Раздел выбора осей, ввода параметров и кнопки запуска программы во вкладке "Создание вектора"
        xAxisLabel = ttk.Label(self, text="Выберите базовую ось X:")
        xAxisLabel.place(relx=0.5, y=120, anchor="n")

        xAxisValues=[]
        self.xAxisCombobox = ttk.Combobox(self, values=xAxisValues, state='readonly')
        self.xAxisCombobox.place(relx=0.5, y=150, anchor="n")
        self.xAxisCombobox.config(width=40)
        Vector.comboboxes.append(self.xAxisCombobox)

        xAxisVector = ttk.Label(self, text="Введите вектор Х:")
        xAxisVector.place(relx=0.5, y=180, anchor="n")

        self.xAxisVector = ttk.Entry(self)
        self.xAxisVector.place(relx=0.5, y=210, anchor="n")
        self.xAxisVector.config(width=40)
        Vector.entries.append(self.xAxisVector)

        #Список для отображения переменных
        variableList = tk.Listbox(self)
        variableList.bind("<Double-Button-1>", lambda _:self.insert_variable(variableList, self.formulaEntry))
        variableList.place(relx=0.5, y=305, anchor="n")

        formulaLabel = ttk.Label(self, text="Введите формулу.")
        formulaLabel.place(relx=0.5, y=245, anchor="n")

        formulaLabelD = ttk.Label(self, text="Y =")
        formulaLabelD.place(relx=0.1, y=270, anchor="n")

        self.formulaEntry = ttk.Entry(self)
        self.formulaEntry.place(relx=0.5, y=270, anchor="n")
        self.formulaEntry.config(width=40)
        #<KeyRelease> - отпускание клавиши
        self.formulaEntry.bind("<KeyRelease>", lambda _:self.show_variable_list(self.path, self.formulaEntry, variableList))
        # <ButtonRelease-1> - отпускание клавиши
        self.formulaEntry.bind("<ButtonRelease-1>",
                               lambda _: self.show_variable_list(self.path, self.formulaEntry, variableList))
        #"<FocusIn>" - фокус на виджете
        self.formulaEntry.bind("<FocusIn>", lambda _:self.show_variable_list(self.path, self.formulaEntry, variableList))
        Vector.entries.append(self.formulaEntry)

        runButton = ttk.Button(self, text="Запустить программу", command=self.run)
        runButton.place(relx=0.5, y=480, anchor="n")
        runButton.config(width=25)

        copyButton = ttk.Button(self, text="Скопировать результат", command=lambda :self.copy_to_clipboard(self.csvRecordList))
        copyButton.place(relx=0.5, y=510, anchor="n")
        copyButton.config(width=25)

        downloadButton = ttk.Button(self, text="Скачать таблицу", command=lambda :self.download_file(self.csvRecordList))
        downloadButton.place(relx=0.5, y=540, anchor="n")
        downloadButton.config(width=25)

    def run(self):
        # ПРОВЕРКИ
        xAxis = self.xAxisCombobox.get()
        if len(xAxis) == 0:
            messagebox.showerror('Ошибка', 'Не задана ось Х.')
            return

        if not self.xAxisVector.get():
            messagebox.showerror('Ошибка', 'Неверное задан вектор Х.')
            return

        formula = self.formulaEntry.get()
        try:
            ast.parse(formula)
        except SyntaxError:
            messagebox.showerror('Ошибка', 'Формула не корректна.')
            return

        # ПРОГРАММА
        xAxisVector = self.xAxisVector.get()
        xAxisVector = re.findall(r'-?\b\d+(?:\.\d+)?\b', xAxisVector)
        if len(xAxisVector) < 3:
            messagebox.showerror('Ошибка', 'Вектор X должен содержать минимум 3 значения.')
            return

        dataFromFile = lib_data_csv.file_read_lines(self.path)
        strArr = dataFromFile
        strArr = strArr[0].split(";")  # Добавили только заголовки
        for iter in range(0, len(strArr)):
            if (xAxis == strArr[iter]) or (xAxis == strArr[iter][:-1]):
                columnX = iter
        columnY = None
        tempArr = strArr  # Добавили только заголовки
        for iter in range(0, len(strArr)):
            tempArr[iter] = tempArr[iter].split(",")[0]
            tempArr[iter] = tempArr[iter].split(" ")[0]  # Разделяем заголовок по " " и присваиваем часть до " "
        dataArr = lib_common.data_arr_creating(dataFromFile)
        arrZ = app_vector.columnZ_creating(dataArr, formula, tempArr)
        pointsArr = app_vector.points_arr_creating(dataArr, columnX, columnY, arrZ)
        for point in pointsArr:
            point.Y = point.Z

        sortedPoints = app_vector.points_sort_vector(xAxisVector, pointsArr)
        counter = 0
        for iter in range(len(sortedPoints)):
            for jter in range(len(sortedPoints[iter])):
                if len(sortedPoints[iter][jter]) == 1:
                    counter = 1
        if counter == 1:
            messagebox.showerror('Ошибка', 'Между каждых соседних значений вектора должна быть хотя бы одна точка.')
            return
        avgPointsArr = app_vector.avg_sorted_points_vector(sortedPoints)
        csvRecord = app_vector.replace_symbols_surface(avgPointsArr, '.', ',')
        self.csvRecordList = app_vector.process_list_to_csvFormat_surface(csvRecord)
        csvRecord = app_vector.replace_symbols_surface(avgPointsArr, ',', '.')
        app_vector.vector_creating(avgPointsArr, xAxisVector, pointsArr, strArr[columnX])

class Application(tk.Tk):
    tabArr=[]
    def __init__(self):
        super().__init__()

        self.title("GUI version 1.03")
        self.geometry("800x800+{}+{}".format(self.winfo_screenwidth() // 2 - 400, self.winfo_screenheight() // 2 - 400))

        # Создание вкладок
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="y")

        surfaceTab = Surface(self.notebook, tabTitle="Создание поверхности")
        approximationTab = Approximation(self.notebook, tabTitle="Аппроксимация")
        vectorTab = Vector(self.notebook, tabTitle="Построение вектора")

        Application.tabArr.append(surfaceTab)
        Application.tabArr.append(approximationTab)
        Application.tabArr.append(vectorTab)

        self.notebook.add(surfaceTab, text=surfaceTab.tabTitle)
        self.notebook.add(approximationTab, text=approximationTab.tabTitle)
        self.notebook.add(vectorTab, text=vectorTab.tabTitle)

        for tab in Application.tabArr:
            cfg.CustomConfig().get_cfg_data(tab)
        try:
            self.protocol("WM_DELETE_WINDOW", lambda: cfg.CustomConfig().create(Application.tabArr, self))
        except Exception as e:
            messagebox.showerror('Ошибка', f'Ошибка с записью файла cfg: {e}')
            self.destroy() # закрытие окна
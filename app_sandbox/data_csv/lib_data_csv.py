############################### Libraries ######################################
import pathlib #библиотека для работы с файлами
import os #os.path - библиотека для работы с путями
import sys
import common.lib_common as lib_common
import gui.gui_sandbox as gui_sandbox
############################### Functions ######################################
def file_read_lines(filePath):
    encodingFile = 'windows-1251'
    if(os.path.exists(filePath) == True): #существует ли файл по этому пути
        strArr = []
        try:
            fo = open(filePath, "r+", encoding=encodingFile)
        except IOError:
            gui_sandbox.messagebox.showerror('Ошибка', f'Открыт файл {filePath}')
            return 0
        #fo = open(filePath, "r+", encoding=encodingFile)

        lineStr = " "
        strArr.append(lineStr)
        while lineStr:
            lineStr = fo.readline()
            strArr.append(lineStr)
        strArr = strArr[1:len(strArr)]
    else:
        print("ERROR: filePath=" + filePath + " is invalid!")
        sys.exit()
    return strArr

#записываем буффер в файл
def file_write_buf(filePath, strBuf):
    encodingFile = 'windows-1251'
    outDir = os.path.split(filePath)[0]
    pathlib.Path(outDir).mkdir(parents=True, exist_ok=True)
    fo = open(filePath, "w+", encoding=encodingFile)
    fo.write(strBuf)
    fo.close()
    return

#преобразование списка в строку, которую можно записать в файл
def process_list_to_csvFormat(csvRecordList):
    listBuf = []
    strBuf = ""
    for csvRecord in csvRecordList:
        if (csvRecord != None):
            for iter in range(0, len(csvRecord)):
                if (iter == len(csvRecord) - 1) and (str(csvRecord[iter][-1]) != '\n'):
                    strBuf += str(csvRecord[iter]) + "\n"
                else:
                    if str(csvRecord[iter][-1]) != '\n':
                        strBuf += str(csvRecord[iter]) + ";"
                    else:
                        strBuf += str(csvRecord[iter])
            listBuf.append(strBuf)
            strBuf = ""
    return listBuf

#генерируем список в csv файл и записываем
def generate_csv_file(csvRecordList):
    strBuf = ""
    for csvRecord in csvRecordList:
        if(csvRecord != None):
                strBuf += str(csvRecord)
    return strBuf

#преобразовываем файл в список, с которым будет выполняться дальнейшая работа
def process_csv_file(file):
    csvRecordList = []
    csvStrList = file_read_lines(file)
    csvRecordList = lib_common.data_arr_creating(csvStrList)
    return csvRecordList

#генерируем список в массив для копирования в буфер обмена
def generate_csv_buf(csvRecordList):
    arrBuf = []
    strBuf = ""

    for csvRecord in csvRecordList:
        strArr = csvRecord.split(";")
        arrBuf.extend(strArr)
    
    for csvRecord in arrBuf:
        if csvRecord is not None:
            if csvRecord.endswith('\n'):
                strBuf += csvRecord
            else:
                strBuf += csvRecord + '\t'

    #Обрезаем строку
    if strBuf.endswith('\t') or strBuf.endswith('\n'):
        strBuf = strBuf[:-1]

    return strBuf
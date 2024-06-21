############################### Libraries ######################################
import re
############################### Functions ######################################

# преобразовываем файл в двумерный массив (преобразуем строку в массив данных)
# заменяем запятые на точки
def data_arr_creating(strArr):
    dataArr = []
    for iter in range(1, len(strArr)):
        dataArr.append(strArr[iter].split(";"))
        for jter in range(0, len(dataArr[iter - 1])):
            dataArr[iter - 1][jter] = dataArr[iter - 1][jter].replace(",", ".")
    return dataArr

#проверка существования регулярного выражения
def regex_search(inputStr, pattern):
    foundObj = re.search(r'' + pattern, inputStr, re.MULTILINE | re.I)
    return foundObj

# замена символа в двумерном массиве. Заменяем символ 1 на символ 2
# Преобразование массива float в str
def replace_symbols(dataArr, s_1, s_2):
    dataArrStr = [[]]
    for iter in range(0, len(dataArr)):
        for jter in range(0, len(dataArr[iter])):
            if dataArr[iter][jter]:
                dataArr[iter][jter] = str(dataArr[iter][jter]).replace(s_1, s_2)
    dataArrStr = dataArr
    return dataArrStr
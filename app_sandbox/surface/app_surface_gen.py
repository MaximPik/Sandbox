############################### Classes ######################################
class Axis:
    def __init__(self, minValue, maxValue, numCells):
        self.minValue = minValue
        self.maxValue = maxValue
        self.numCells = numCells


class Point:
    def __init__(self, X, Y, Z):
        self.X = X
        self.Y = Y
        self.Z = Z

############################### Libraries ######################################
import math
from tkinter import *  # графический интерфейс
# Для 3д поверхности
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import griddata
import re
import math
from scipy.optimize import curve_fit

############################### Functions ######################################

def columnZ_creating(dataArr, formula, headings):
    columnZ=[]
    currFormula = re.sub(r"['^']", '**', formula)
    formulaWithValue = formula
    parts = re.split(r'[+\-*/()]', currFormula) # разделять формулу на отдельные элементы
    # Поиск переменной и замена ее на значение из массива
    #for iter in range(0, len(dataArr)-1):
    for row in dataArr:
        row[-1] = row[-1][:-1] #Удаляем "\n" в последнем элементе строки
        if len(row)>1:
            counter = 0
            currFormula = formula
            for name in headings:
                counter += 1
                for jter in range(0, len(parts)):
                    if name == parts[jter]:
                        formulaWithValue = re.sub(name, str(row[counter - 1]), currFormula)
                        currFormula = formulaWithValue
            formulaWithValue = re.sub(r"['^']", '**', formulaWithValue)
            columnZ.append(eval(formulaWithValue, {"__builtins__": None}, {"sqrt": math.sqrt}))
    return columnZ

# создаём массив точек
def points_arr_creating(dataArr, columnX, columnY, arrZ):
    pointsArr = []
    counter = 0
    for row in dataArr:
        counter += 1
        if columnY != None:
            if len(row) >= 2 and row[columnX] and row[columnY]:  # проверка на наличие символов
                point = Point(row[columnX], row[columnY], arrZ[counter-1])
                pointsArr.append(point)
            else:
                counter -= 1
        else:
            if len(row) >= 2 and row[columnX]:  # проверка на наличие символов
                point = Point(row[columnX], 0, arrZ[counter - 1])
                pointsArr.append(point)
            else:
                counter -= 1
    return pointsArr


# группируем точки по ячейкам
def points_sort(axisXVector, axisYVector, pointsArr):
    #Преобразуем массив строк в числовой
    axisXVector = [float(num) for num in axisXVector]
    axisYVector = [float(num) for num in axisYVector]
    # создаём пустой трёхмерный массив
    sortedPointsArr = [[[0 for kter in range(1)] for jter in range(len(axisYVector)-1)] for iter in range(len(axisXVector)-1)]
    for point in pointsArr:
        cellIndexX = None
        cellIndexY = None
        for cell in range(0, len(axisXVector) - 1):
            if cellIndexX == None:
                if float(point.X) >= axisXVector[cell] and float(point.X) < axisXVector[cell+1]:
                    cellIndexX = cell
        for cell in range(0, len(axisYVector) - 1):
            if cellIndexY == None:
                if float(point.Y) >= axisYVector[cell] and float(point.Y) < axisYVector[cell + 1]:
                    cellIndexY = cell

        if cellIndexX != None and cellIndexY != None:  # проверка выход за диапазон
            sortedPointsArr[cellIndexX][cellIndexY].append(point)

    return sortedPointsArr


# поиск узловых значений
def node_points(axisXVector, axisYVector, sortedPointsArr, zMin, zMax):
    nodePoints = [[0 for jter in range(len(sortedPointsArr[0]))] for iter in range(len(sortedPointsArr))]
    for row in range(0, len(sortedPointsArr)):
        for col in range(0, len(sortedPointsArr[row])):
            summX = 0
            summY = 0
            summZ = 0
            if len(sortedPointsArr[row][col]) > 1:  # Если есть точка
                for point in sortedPointsArr[row][col]:
                    if point != 0:
                        summX = summX + float(point.X)
                        summY = summY + float(point.Y)
                        summZ = summZ + float(point.Z)
                avgX = summX / (len(sortedPointsArr[row][col]) - 1)
                avgY = summY / (len(sortedPointsArr[row][col]) - 1)
                avgZ = summZ / (len(sortedPointsArr[row][col]) - 1)
                nodePoints[row][col] = Point(avgX, avgY, avgZ)
    if all(all(element == 0 for element in row) for row in nodePoints):
        return -1
    else:
        nodePoints = interpolate(sortedPointsArr, axisXVector, axisYVector, zMin, zMax)
        return nodePoints

# Полиномиальная интерполяция/экстраполяция функции двух переменных (новый алгоритм)
# Нахождение коэффициентов при рассмотрении всех точек, а не только средних.
# Выполняется интерполяция/экстраполяция для узловых точек
def interpolate(sortedPointsArr, axisXVector, axisYVector, zMin, zMax):
    axisXVector = [float(num) for num in axisXVector]
    axisYVector = [float(num) for num in axisYVector]
    copyArr = sortedPointsArr  # Вспомогательный
    arrX, arrY, arrZ = [], [], []
    for row in range(0, len(copyArr)):
        for col in range(0, len(copyArr[row])):
            for point in range(0, len(copyArr[row][col])):
                if copyArr[row][col][point] != 0:
                    arrX.append(float(copyArr[row][col][point].X))
                    arrY.append(float(copyArr[row][col][point].Y))
                    arrZ.append(float(copyArr[row][col][point].Z))
    arrX = np.array(arrX)
    arrY = np.array(arrY)
    arrZ = np.array(arrZ)
    axisXVector = np.array(axisXVector)
    axisYVector = np.array(axisYVector)

    # Добавляю к axisXVector и axisYVector по краям значение, чтобы избежать ошибки, когда
    # точки находятся на краях поля
    diffX = (np.sum(np.diff(axisXVector)) / (axisXVector.size-1)) * 2 # среднее значение между ячейками вектора Х * 2
    diffY = (np.sum(np.diff(axisYVector)) / (axisYVector.size-1)) * 2 # среднее значение между ячейками вектора Y * 2
    axisXVector = np.append(axisXVector, axisXVector[-1] + diffX) # добавляем доп. значение в конец
    axisXVector = np.hstack(([axisXVector[0] - diffX], axisXVector)) # добавляем доп. значение в начало
    axisYVector = np.append(axisYVector, axisYVector[-1] + diffY) # добавляем доп. значение в конец
    axisYVector = np.hstack(([axisYVector[0] - diffY], axisYVector)) # добавляем доп. значение в начало

    def func(coords, a, b, c):
        x, y = coords
        return a * x ** 2 + b * y ** 2 + c

    popt, pcov = curve_fit(func, (arrX, arrY), arrZ)

    # Заполняем верхнюю и нижнюю границы
    for iter in range(len(axisXVector) - 1):
        arrX = np.append(arrX, axisXVector[iter + 1])
        arrY = np.append(arrY, axisYVector[0])
        coordZ = func((arrX[-1], arrY[-1]), *popt)
        arrZ = np.append(arrZ, coordZ)

    for iter in range(len(axisYVector) - 1):
        arrX = np.append(arrX, axisXVector[-1])
        arrY = np.append(arrY, axisYVector[iter + 1])
        coordZ = func((arrX[-1], arrY[-1]), *popt)
        arrZ = np.append(arrZ, coordZ)

    for iter in range(len(axisXVector) - 1):
        arrX = np.append(arrX, axisXVector[iter])
        arrY = np.append(arrY, axisYVector[-1])
        coordZ = func((arrX[-1], arrY[-1]), *popt)
        arrZ = np.append(arrZ, coordZ)

    for iter in range(len(axisYVector) - 1):
        arrX = np.append(arrX, axisXVector[0])
        arrY = np.append(arrY, axisYVector[iter])
        coordZ = func((arrX[-1], arrY[-1]), *popt)
        arrZ = np.append(arrZ, coordZ)

    XY = np.stack((arrX, arrY), axis=1)  # (x;2)
    grid_x, grid_y = np.meshgrid(axisXVector, axisYVector)
    grid_z = griddata(XY, arrZ, (grid_x, grid_y), method='linear')

    # Удаляем крайние значения векторов axisXVector и axisYVector
    axisXVector = np.delete(axisXVector, [0, -1])
    axisYVector = np.delete(axisYVector, [0, -1])

    interpArr = [[0 for jter in range(len(axisXVector))] for iter in range(len(axisYVector))]
    interpArr = np.array(interpArr, dtype=object)
    for row in range(0, len(axisYVector)):
        for col in range(0, len(axisXVector)):
            coordZ = grid_z[row + 1][col + 1]
            if zMax != '' and zMin !='':
                if coordZ > zMax: coordZ = zMax
                if coordZ < zMin: coordZ = zMin
            elif zMax != '' and zMin == '':
                if coordZ > zMax: coordZ = zMax
            elif zMax == '' and zMin != '':
                if coordZ < zMin: coordZ = zMin
            # Если нужно ввести ограничение на Z, то нужно ограничить coordZ! Для этого передать в функцию zMin и zMax
            interpArr[row][col] = Point(axisXVector[col], axisYVector[row], coordZ)
    interpArr = interpArr.tolist()
    return interpArr

# преобразование списка в строку, которую можно записать в файл
def process_list_to_csvFormat_surface(avgPointsArr):
    listBuf = []
    strBuf = ""
    for csvRecord in avgPointsArr:
        if (csvRecord != None):
            for iter in range(0, len(csvRecord)):
                if (iter == len(csvRecord) - 1):
                    if csvRecord[iter] != 0:
                        strBuf += str(csvRecord[iter].Z) + "\n"
                    else:
                        strBuf += str(csvRecord[iter]) + "\n"
                else:
                    if csvRecord[iter] != 0:
                        strBuf += str(csvRecord[iter].Z) + ";"
                    else:
                        strBuf += str(csvRecord[iter]) + ";"
            listBuf.append(strBuf)
            strBuf = ""
    return listBuf

# замена символа в двумерном массиве. Заменяем символ 1 на символ 2
# Преобразование массива float в str
def replace_symbols_surface(dataArr, s_1, s_2):
    dataArrStr = [[]]
    for iter in range(0, len(dataArr)):
        for jter in range(0, len(dataArr[iter])):
            if dataArr[iter][jter] != 0:
                dataArr[iter][jter].Z = str(dataArr[iter][jter].Z).replace(s_1, s_2)
    dataArrStr = dataArr
    return dataArrStr


# построение 3д поверхности
def surface(nodePointsTab, pointsArr, axisXVector, axisYVector, zMin, zMax):
    # преобразуем двумерный массив средних точек в 2 одномерных массива координат Х и Y
    arrX = [[0 for jter in range(len(nodePointsTab[0]))] for iter in range(len(nodePointsTab))]
    arrY = [[0 for jter in range(len(nodePointsTab[0]))] for iter in range(len(nodePointsTab))]
    arrZ = [[0 for jter in range(len(nodePointsTab[0]))] for iter in range(len(nodePointsTab))]
    pointsX = []
    pointsY = []
    pointsZ = []
    for row in range(0, len(nodePointsTab)):
        for col in range(0, len(nodePointsTab[row])):
            if nodePointsTab[row][col] != 0:
                arrX[row][col] = nodePointsTab[row][col].X
                arrY[row][col] = nodePointsTab[row][col].Y
                arrZ[row][col] = nodePointsTab[row][col].Z
    for row in range(0, len(pointsArr)):
        pointsX.append(float(pointsArr[row].X))
        pointsY.append(float(pointsArr[row].Y))
        pointsZ.append(float(pointsArr[row].Z))

    # Создаём 3д график
    fig = plt.figure()
    arrX = np.array(arrX)
    arrY = np.array(arrY)
    arrZ = np.array(arrZ)
    ax = fig.add_subplot(111, projection='3d')
    # Строим каркасную поверхность
    ax.plot_surface(arrX, arrY, arrZ, color='blue', rstride=1, cstride=1, edgecolor='black', linewidth=0.5, alpha=0.5)
    # Наносим множество точек
    ax.scatter(pointsX, pointsY, pointsZ, s=0.3, color='red')

    # Преобразуем массив строк в числовой
    axisXVector = [float(num) for num in axisXVector]
    axisYVector = [float(num) for num in axisYVector]
    arrZ = arrZ.astype(float)
    maxValX = max(axisXVector)  # максимальное Х из массива точек
    maxValY = max(axisYVector)  # максимальное Y из массива точек
    minValX = min(axisXVector)  # минимальное Х из массива точек
    minValY = min(axisYVector)  # минимальное Y из массива точек
    maxValZ = np.max(arrZ) # максимальное Z из массива точек
    minValZ = np.min(arrZ) # минимальное Z из массива точек

    ax.set_xlim(float(minValX), float(maxValX))
    ax.set_ylim(float(minValY), float(maxValY))
    if zMax != '' and zMin != '':
        ax.set_zlim(float(zMin), float(zMax))
    elif zMax != '' and zMin == '':
        ax.set_zlim(float(minValZ), float(zMax))
    elif zMax == '' and zMin != '':
        ax.set_zlim(float(zMin), float(maxValZ))

    # Название осей
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    plt.show()

def format_func(value, tick_number):
    if value >= 100000:
        return '{:,.0f}'.format(value)  # Отображение полных значений с разделителями
    else:
        return '{:.2f}'.format(value)  # Отображение значений с двумя знаками после запятой
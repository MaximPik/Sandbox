############################### Libraries ######################################
import matplotlib.pyplot as plt
import numpy as np
import surface.app_surface_gen as app_surface_gen

############################### Functions ######################################
def vector_creating(avgPointsArr, axisXVector, pointsArr, nameAxisX):
    arrX = []
    arrY = []
    pointsX = []
    pointsZ = []
    axisXVector = [float(num) for num in axisXVector]
    for row in range(0, len(pointsArr)):
        pointsX.append(float(pointsArr[row].X))
        pointsZ.append(float(pointsArr[row].Z))
    #созданим отдельно массивы координат
    for iter in range(0, len(avgPointsArr[0])):
        arrX.append(float(avgPointsArr[0][iter].X))
        arrY.append(float(avgPointsArr[0][iter].Z))
    arrX = np.array(arrX)
    arrY = np.array(arrY)
    maxValX = max(axisXVector)  # максимальное Х из массива точек
    minValX = min(axisXVector)  # минимальное X из массива точек
    maxValY = max(arrY)  # максимальное Х из массива точек
    minValY = min(arrY)  # минимальное X из массива точек
    plt.grid()  # Добавляем сетку
    plt.xlabel(nameAxisX)
    plt.ylabel('Y')
    plt.xlim(minValX, maxValX)  # Максимальное и минимальное значение оси x
    plt.ylim(minValY, maxValY)  # Максимальное и минимальное значение оси y
    plt.scatter(pointsX, pointsZ, s=1, color='red')
    plt.plot(arrX, arrY, color='blue')  # Строим вектор
    plt.show()
# группируем точки по ячейкам
def points_sort_vector(axisXVector, pointsArr):
    # создаём пустой трёхмерный массив
    sortedPointsArr = [[[0 for kter in range(1)] for jter in range(len(axisXVector)-1)] for iter in range(1)]
    #cellsWidth = (axisX.maxValue - axisX.minValue) / axisX.numCells  # ширина ячейки
    axisXVector = [float(num) for num in axisXVector]
    for point in pointsArr:
        cellIndexX = None
        for cell in range(0, len(axisXVector) - 1):
            if cellIndexX == None:
                if float(point.X) >= axisXVector[cell] and float(point.X) < axisXVector[cell+1]:
                    cellIndexX = cell
        if cellIndexX != None:  # проверка выход за диапазон
            sortedPointsArr[0][cellIndexX].append(point)

    return sortedPointsArr

# поиск среднего значение группированных точек каждой ячейки
def avg_sorted_points_vector(sortedPointsArr):
    avgPointsArr = [[0 for jter in range(len(sortedPointsArr[0]))] for iter in range(len(sortedPointsArr))]
    for row in range(0, len(sortedPointsArr)):
        for col in range(0, len(sortedPointsArr[row])):
            summX = 0
            summZ = 0
            if len(sortedPointsArr[row][col]) > 1:  # Если есть точка
                for point in sortedPointsArr[row][col]:
                    if point != 0:
                        summX = summX + float(point.X)
                        summZ = summZ + float(point.Z)
                avgX = summX / (len(sortedPointsArr[row][col]) - 1)
                avgZ = summZ / (len(sortedPointsArr[row][col]) - 1)
                avgPointsArr[row][col] = app_surface_gen.Point(avgX, 0, avgZ)

    return avgPointsArr
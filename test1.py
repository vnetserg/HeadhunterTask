#!/usr/bin/python3.4

'''
    Файл с тестом решения первой задачи.
    Результат, полученный через структуру данных
    Kd-Tree проверяется наивной реализацией
    решения поставленной задачи.
'''

import math, random, argparse
from task1 import KdTree, parse_file

def radius_and_neighbors_tree(points):
    '''
        Найти радиус и число соседей каждой точки из
        списка с помощью структуры данных Kd-Tree.
        Вернуть словарь, в котором ключи - точки,
        а значения - кортежи (радиус, число_соседей).
        Аргументы:
            points - список кортежей (x,y)
    '''
    random.seed("TrFtqH1MGAEZigu5") # для воспроизводимости
    random.shuffle(points) # чтобы иметь статистически сбалансированное дерево
    tree = KdTree()
    for point in points:
        tree.addPoint(point)
    return {point: tree.getRadiusAndNeighbors(point) for point in points}

def distance_to(p1, p2):
    '''
        Вернуть расстояние между точками. Аргументы:
            p1, p2 - кортежи значений (x,y)
    '''
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

def radius_and_neighbors_naive(points):
    '''
        Найти радиус и число соседей каждой точки из
        списка. Наивная реализация, сложность O(n^2).
        Вернуть словарь, в котором ключи - точки,
        а значения - кортежи (радиус, число_соседей).
        Аргументы:
            points - список кортежей (x,y)
    '''
    result = {}
    for point in points:
        radius = None
        for other in points:
            dist = distance_to(point, other)
            if dist != 0 and (radius is None or radius > dist):
                radius = dist
        neighbors = 0
        for other in points:
            dist = distance_to(point, other)
            if radius <= dist <= 2*radius:
                neighbors += 1
        result[point] = (radius, neighbors)
    return result

def mismatches(points):
    '''
        Сопоставить результаты, поулчаемые на данном наборе
        точек методом KdTree и наивным методом. При
        возникновении несоответствий записать их в
        словарь в формате
            {точка: ((радиус1, соседи1),(радиус2, соседи2))}
        и вернуть этот словарь. Аргументы:
            points - список кортежей (x,y)
    '''
    errs = {}
    res1 = radius_and_neighbors_naive(points)
    res2 = radius_and_neighbors_tree(points)
    for point in points:
        if res1[point] != res2[point]:
            errs[point] = (res1[point], res2[point])
    return errs

def minimum_error_set(points):
    '''
        Вернуть минимальной длины список точек,
        в котором наблюдаются несоответствия между
        результатами метода KdTree и наивного
        метода.
    '''
    while mismatches(points):
        last = list(points)
        points.remove(random.choice(points))
    return last

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="file with list of points", type=str)
    args = parser.parse_args()
    points = parse_file(args.file)
    if not points:
        return
    if len(mismatches(points)) == 0:
        print("OK")
    else:
        errset = minimum_error_set(points)
        errs = mismatches(errset)
        txt = "\n".join(["{} {}".format(*p) for p in errset])
        with open("minerr.txt", "w") as f:
            f.write(txt)
        print("ERROR. Minimum error set written to 'minerr.txt'. Length: {}".format(len(errset)))
        print("MISMATCHES: {}".format("; ".join(["{}: {} vs {}".format(pt, res1, res2)
            for pt, (res1, res2) in errs.items()])))

if __name__ == "__main__":
    main()
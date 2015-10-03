#!/usr/bin/python3.4

'''
    Файл с решением первой задачи.

    ЗАДАЧА:
    Даны N точек на плоскости. Назовём расстояние от точки A
    до ближайщей к ней точки B "радиусом" точки A. "Соседями"
    точки A будем называть все точки, лежащие в пределах
    двойного радиуса от неё включительно.
    Для каждой точки из заданного набора определите её радиус
    и количество соседей.

    ФОРМАТ ВХОДНЫХ ДАННЫХ:
    Первый и единственный аргумент программы - путь к файлу,
    в котором лежит список точек.
    Формат файла: координаты точки должны быть указаны
    через пробел, каждая точка на отдельной строке.

    ФОРМАТ ВЫХОДНЫХ ДАННЫХ:
    Для каждой точки в стандартный вывод печатается строка формата:
    (x, y): radius {float}, neighbors {int}

    Описание алгоритма решения приведено в README.
'''

import math, random, argparse
from queue import Queue, PriorityQueue

class KdTree:
    '''
        Класс, реализующий структуру данных Kd-Tree.
    '''

    def __init__(self):
        self.root = None # корневой узел дерева

    def addPoint(self, point):
        '''
            Добавить точку в структуру данных. Аргументы:
                point - кортеж координат (x,y)
        '''
        if self.root is None:
            self.root = Node(point)
        else:
            self._findNode(point).addLeaf(point)

    def getRadiusAndNeighbors(self, point):
        '''
            Вернуть радиус и число соседей заданной точки.
            Аргументы:
                point - кортеж координат (x,y)
        '''
        node = self._findNode(point)
        if node.point != point:
            raise ValueError("Point not in tree")
        closest, radius = self._closestNeighbor(node.point)
        all_points = self._rangeSearch(Rectangle.centeredIn(
            point, 4*radius, 4*radius))
        neighbors = [point for point in all_points
            if radius <= node.distanceTo(point) <= 2*radius]
        return radius, len(neighbors)

    def _findNode(self, point):
        '''
            Если точка есть в дереве, найти её узел. Если точки
            нет, найти родительский узел, после которого данная
            точка должна быть вставлена. Аргументы:
                point - кортеж координат (x,y)
        '''
        if self.root is None:
            raise ValueError("No nodes to search")
        node = self.root
        while node.next(point) is not None:
            if node.point == point:
                return node
            node = node.next(point)
        return node

    def _closestNeighbor(self, point):
        '''
            Найти ближайщего соседа данной точки. Если
            узел с координатами этой точки есть в дереве,
            при поиске соседа он игнорируется. Аргументы:
                point - кортеж координат (x,y)
        '''
        
        min_distance = None
        min_node = None

        # Формируем приоритетную очередь по принципу
        # "чем ближе прямоугольник узла к данной
        # точке - тем лучше".
        queue = PriorityQueue()
        queue.put((0, self.root)) # начинаем обход с корневого узла

        while not queue.empty():
            dist_to_rect, node = queue.get()

            dist_to_point = node.distanceTo(point)
            if dist_to_point > 0 and (min_distance is None or dist_to_point < min_distance):
                min_distance = dist_to_point
                min_node = node
            elif min_distance is not None and dist_to_rect > min_distance:
                # Условие отсечения ветви поиска: если
                # все потомки данного узла заведомо
                # дальше от исходой точки, чем уже
                # найденный ближайший узел
                continue

            for child in (node.left, node.right):
                if child is None:
                    continue
                queue.put((child.rect.distanceTo(point), child))
        return min_node, min_distance

    def _rangeSearch(self, rect):
        '''
            Поиск всех точек, лежащих в прямоугольном диапазоне.
            Аргументы:
                rect - объект Rectangle
        '''
        queue = Queue() # очередь узлов, в потомках которых
                        # потенциально есть искомые точки
        queue.put(self.root)
        result = [] # список найденных точек
        while not queue.empty():
            node = queue.get()
            if rect.hasInside(node.point):
                result.append(node.point)
            for child in (node.left, node.right):
                if child is not None and child.rect.intersectsWith(rect):
                    queue.put(child)
        return result

class Node:
    '''
        Класс, реулизующий узел структуры данных Kd-Tree.
    '''

    def __init__(self, point, coord=0, rect=None):
        '''
            point - кортеж координат (x,y)
            coord - координата разбиения потомков: 0 - х, 1 - у
            rect  - прямоугольник, в котором лежат все потомки
                    данного узла
        '''
        self.point = point
        self.coord = coord
        if rect is not None:
            self.rect = rect
        else:
            self.rect = Rectangle() # бесконечный прямоугольник
        self.left = None # левый дочерний узел
        self.right = None # правый дочерний узел
    
    def __lt__(self, other):
        '''
            Сравнить два узла по координатам их точек.
            Метод нужен для корректной работы PriorityQueue.
        '''
        if not isinstance(other, Node):
            raise ValueError("Unorderable types: Node() < {}()".format(other.__class__.__name__))
        return self.coord < other.coord
    
    def next(self, point):
        '''
            Вернуть следующий узел, в потомках которого может
            находиться данная точка. Вернуть None, если
            соответствующий узел ещё не существует. Аргументы:
                point - кортеж координат (x,y)
        '''
        assert self.rect.hasInside(point)
        if point[self.coord] < self.point[self.coord]:
            return self.left
        return self.right

    def addLeaf(self, point):
        '''
            Добавить точку как дочерний узел и вернуть добавленный
            узел. Аргументы:
                point - кортеж координат (x,y)
        '''
        ind = int(point[self.coord] >= self.point[self.coord])
        rect = self.rect.split(self.point[self.coord], coord=self.coord)[ind]
        leaf = Node(point, (self.coord+1)%2, rect=rect)
        if ind == 0:
            assert self.left is None
            self.left = leaf
        else:
            assert self.right is None
            self.right = leaf
        return leaf

    def distanceTo(self, point):
        '''
            Вернуть расстояние от точки узла до заданной точки.
            Аргументы:
                point - кортеж координат (x,y) либо объект Node
        '''
        if isinstance(point, Node):
            point = point.point
        return math.sqrt((self.point[0]-point[0])**2 + (self.point[1]-point[1])**2)

class Rectangle:
    '''
        Класс, реализующий прямоугольную область на плоскости.
        Область может быть ограничена менее, чем с четырёх сторон.
    '''
    
    def __init__(self, coords=None):
        '''
            coords - список отрезков, ограничивающих область
                     по каждой координате: [(x1,x2), (y1,y2)].
                     None вместо координаты означает отсутствие
                     соответствюущего ограничения.
        '''
        if coords is not None:
            for pair in coords:
                assert len(pair) == 2
                if all(crd is not None for crd in pair):
                    assert pair[0] <= pair[1]
            self.coords = coords
        else:
            # Бесконечный прямоугольник:
            self.coords = [(None, None), (None, None)]

    @classmethod
    def centeredIn(cls, center, width, height):
        '''
            Вернуть прямоугольник с центром в center, шириной
            width и высотой height. Аргументы:
                point  - кортеж координат (x,y)
                width  - ширина прямоугольника
                height - высота прямоугольника
        '''
        return cls([(center[0]-width/2, center[0]+width/2),
                       (center[1]-height/2, center[1]+height/2)])

    def distanceTo(self, point):
        '''
            Вернуть кратчайшее расстояние от заданной точки
            до данного прямоугольника. Аргументы:
                point - кортеж координат (x,y)
        '''
        if self.coords[0][0] is not None and point[0] < self.coords[0][0]:
            x = self.coords[0][0]
        elif self.coords[0][1] is not None and self.coords[0][1] < point[0]:
            x = self.coords[0][1]
        else:
            x = point[0]
        if self.coords[1][0] is not None and point[1] < self.coords[1][0]:
            y = self.coords[1][0]
        elif self.coords[1][1] is not None and self.coords[1][1] < point[1]:
            y = self.coords[1][1]
        else:
            y = point[1]
        return math.sqrt((point[0]-x)**2 + (point[1]-y)**2)

    def intersectsWith(self, rect):
        '''
            Вернуть True, если прямоугольники пересекается,
            и False в противном случае. Аргументы:
                rect - объект Rectangle
        '''
        def segments_intersect(seg1, seg2):
            # Пересекаются ли два отрезка
            if seg1 == (None, None) == seg2:
                return True
            for first, second in [(seg1, seg2), (seg2, seg1)]:
                x1, x2 = first
                for vertex in second:
                    if vertex is not None and (x1 is None or x1 <= vertex) and (x2 is None or vertex <= x2):
                        return True
            return False
        return segments_intersect(self.coords[0], rect.coords[0]) and \
            segments_intersect(self.coords[1], rect.coords[1])

    def hasInside(self, point):
        '''
            Вернуть True, если данная точка находится внутри
            прямоугольника, иначе False. Аргументы:
                point - кортеж координат (x,y)
        '''
        for coord in range(2):
            if self.coords[coord][0] is not None and point[coord] < self.coords[coord][0]:
                return False
            if self.coords[coord][1] is not None and self.coords[coord][1] < point[coord]:
                return False
        return True

    def split(self, value, coord):
        '''
            Вернуть разбиение прямоугольника на два. Аргументы:
                value - значение координаты разбиения
                coord - номер координаты разбиения
        '''
        assert self.coords[coord][0] is None or self.coords[coord][0] <= value
        assert self.coords[coord][1] is None or value <= self.coords[coord][1]
        r1 = Rectangle([self.coords[crd] if crd != coord
                        else (self.coords[crd][0], value) for crd in range(2)])
        r2 = Rectangle([self.coords[crd] if crd != coord
                        else (value, self.coords[crd][1]) for crd in range(2)])
        return r1, r2

def parse_file(file):
    '''
        Прочитать файл и вернуть список точек, в нём указанных.
        Если в процессе чтения произошли ошибки, напечатать
        сообщения об ошибках и вернуть None.
    '''
    with open(file, "r") as f:
        lines = f.readlines()
    try:
        res = [tuple(float(x) for x in line.split()) for line in lines if line.strip()]
    except ValueError:
        return print("Error: invalid file format")
    if any(len(pair) != 2 for pair in res):
        return print("Error: expected 2 digits on a line")
    if len(res) < 2:
        return print("Error: at least 2 points expected")
    if len(set(res)) != len(res):
        return print("Error: duplicate points are not supported")
    return res

def main():
    # Точка входа программы
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="file with list of points", type=str)
    args = parser.parse_args()
    points = parse_file(args.file)
    if not points:
        return
    random.seed("TrFtqH1MGAEZigu5") # для воспроизводимости
    random.shuffle(points) # чтобы иметь статистически сбалансированное дерево
    tree = KdTree()
    for point in points:
        tree.addPoint(point)
    for point in sorted(points):
        print("{}: radius {}, neighbors {}".format(point, *tree.getRadiusAndNeighbors(point)))

if __name__ == "__main__":
    main()
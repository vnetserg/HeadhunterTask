#!/usr/bin/python3.4

import math, argparse
from queue import Queue, PriorityQueue

class KdTree:
    def __init__(self):
        self.root = None

    def addPoint(self, point):
        if self.root == None:
            self.root = Node(point)
        else:
            closest, distance = self._closestNeighbor(point)
            new = self._findNode(point).addLeaf(point)
            if closest.radius is None or closest.radius > distance:
                closest.radius = distance
            new.radius = distance

    def getRadiusAndNeighbors(self, point):
        node = self._findNode(point)
        #print("Searching point: {}\nNode point: {}".format(point, node.point))
        #print("Left: {}\nRight: {}".format(node.left, node.right))
        if node.point != point:
            raise ValueError("Point not in tree")
        all_points = self._rangeSearch(Rectangle.centeredIn(point, 4*node.radius, 4*node.radius))
        neighbors = [point for point in all_points if node.radius <= node.distanceTo(point) <= 2*node.radius]
        return node.radius, len(neighbors)

    def _findNode(self, point):
        if self.root is None:
            raise ValueError("No nodes to search")
        node = self.root
        while 1:
            if node.point == point:
                return node
            next_node = node.next(point)
            if next_node is None:
                return node
            node = next_node

    def _closestNeighbor(self, point):
        if self.root is None:
            raise ValueError("No nodes to search")
        min_distance = self.root.distanceTo(point)
        min_node = self.root
        queue = PriorityQueue()
        queue.put((0, self.root))
        while not queue.empty():
            prior, node = queue.get()
            if node.rect.distanceTo(point) > min_distance:
                continue
            for child in (node.left, node.right):
                if child is None:
                    continue
                dist = child.distanceTo(point)
                if dist < min_distance:
                    min_distance = dist
                    min_node = child
                queue.put((child.rect.distanceTo(point), child))
        return min_node, min_distance

    def _rangeSearch(self, rect):
        queue = Queue()
        queue.put(self.root)
        result = []
        while not queue.empty():
            node = queue.get()
            if rect.hasInside(node.point):
                result.append(node.point)
            for child in (node.left, node.right):
                if child is not None and child.rect.intersectsWith(rect):
                    queue.put(child)
        return result

class Node:
    def __init__(self, point, coord=0, rect=None):
        self.point = point
        self.coord = coord
        if rect is not None:
            self.rect = rect
        else:
            self.rect = Rectangle() # бесконечный прямоугольник
        self.left = None
        self.right = None
        self.radius = None
    
    def next(self, point):
        if point[self.coord] < self.point[self.coord]:
            return self.left
        return self.right

    def addLeaf(self, point):
        ind = int(point[self.coord] >= self.point[self.coord])
        rect = self.rect.split(point[self.coord], coord=self.coord)[ind]
        leaf = Node(point, (self.coord+1)%2, rect=rect)
        if ind == 0:
            assert self.left is None
            self.left = leaf
        else:
            assert self.right is None
            self.right = leaf
        return leaf

    def distanceTo(self, point):
        if isinstance(point, Node):
            point = point.point
        return math.sqrt((self.point[0]-point[0])**2 + (self.point[1]-point[1])**2)

class Rectangle:
    def __init__(self, coords=None):
        if coords is not None:
            self.coords = coords
        else:
            self.coords = [(None, None), (None, None)]

    @classmethod
    def centeredIn(cls, center, width, height):
        return cls([(center[0]-width/2, center[0]+width/2),
                       (center[1]-height/2, center[1]+height/2)])

    def distanceTo(self, point):
        if self.coords[0][0] is not None and point[0] < self.coords[0][0]:
            x = self.coords[0][0]
        elif self.coords[0][1] is not None and self.coords[0][1] < point[0]:
            x = self.coords[0][1]
        else:
            x = point[0]
        if self.coords[1][0] is not None and point[1] < self.coords[1][0]:
            y = self.coords[1][0]
        elif self.coords[1][1] is not None and self.coords[1][1] > point[1]:
            y = self.coords[1][1]
        else:
            y = point[1]
        return math.sqrt((point[0]-x)**2 + (point[1]-y)**2)

    def intersectsWith(self, rect):
        for corner in self._corners():
            if rect.hasInside(corner):
                return True
        for corner in rect._corners():
            if self.hasInside(corner):
                return True
        return False

    def hasInside(self, point):
        for coord in range(2):
            if self.coords[coord][0] is not None and point[coord] < self.coords[coord][0]:
                return False
            if self.coords[coord][1] is not None and self.coords[coord][1] < point[coord]:
                return False
        return True

    def split(self, value, coord):
        assert self.coords[coord][0] is None or self.coords[coord][0] <= value
        assert self.coords[coord][1] is None or value <= self.coords[coord][1]
        r1 = Rectangle([self.coords[crd] if crd != coord
                        else (self.coords[crd][0], value) for crd in range(2)])
        r2 = Rectangle([self.coords[crd] if crd != coord
                        else (value, self.coords[crd][1]) for crd in range(2)])
        return r1, r2

    def _corners(self):
        for x in self.coords[0]:
            if x is None: continue
            for y in self.coords[1]:
                if y is None: continue
                yield (x, y)

def parse_file(file):
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
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="file with list of points", type=str)
    args = parser.parse_args()
    points = parse_file(args.file)
    if not points:
        return
    tree = KdTree()
    for point in points:
        tree.addPoint(point)
    for point in points:
        print("{}: radius {}, neighbors {}".format(point, *tree.getRadiusAndNeighbors(point)))

if __name__ == "__main__":
    main()
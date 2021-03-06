# Тестовое задание Школы Программистов HeadHunter
Автор решения: Фомин Сергей.

## Задача №1
### Условие задачи
Даны N точек на плоскости. Назовём расстояние от точки A
до ближайщей к ней точки B "радиусом" точки A. "Соседями"
точки A будем называть все точки, лежащие в пределах
двойного радиуса от неё включительно.
Для каждой точки из заданного набора определите её радиус
и количество соседей.

### Формат входных данных
Первый и единственный аргумент программы - путь к файлу,
в котором лежит список точек.
Формат файла: координаты точки должны быть указаны
через пробел, каждая точка на отдельной строке. 
Для примера см. "points.txt".
Пример использования программы:
`./task1.py points.txt`

### Формат выходных данных
Для каждой точки в стандартный вывод печатается строка формата:

`(x, y): radius {float}, neighbors {int}`

Например:

`(3.0, 3.0): radius 1.0, neighbors 2`

### Алгоритм решения
Для решения задачи использована структура данных Kd Tree,
поскольку она позволяет быстро совершать следующие операции:
* Найти ближайшего соседа любой точки за O(log N)
  операций в среднем и O(N) в худшем случае
  (здесь N - число точек);
* Найти все точки, лежащие в заданной прямоугольной области,
  за O(M + log N) операций в среднем и O(N) в худшем случае
  (здесь N - общее количество точек, M - число точек в
  заданной области)

Чтобы статистически гарантировать выполнение данных операций
за логарифмическое время, поданный на вход программы список
точек случайным образом перемешивается.

Таким образом, данный алгоритм решения задачи имеет сложность
O(N log N), т. к. данные операции небходимо выполнить для
каждой точки.


## Задача №2
### Условие задачи
Для данных натуральных чисел n и k определите
количество способов представить число n в виде суммы k
натуральных слагаемых, если способы, отличающиеся только
порядком слагаемых, считать одинаковыми. Числа n и k
не превосходят 150.

### Формат входных данных
Программа получает на вход два целочисленных аргумента -
числа n и k. Пример использования:

`./task2.py 6 3`

### Формат выходных данных
В стандартный вывод печатается целое число, являющееся ответом.

### Алгоритм решения
Для решения задачи была использована следующая рекуррентная формула:

`p(n,k) = p(n-1, k-1) + p(n-k, k)`

Граничные условия рекурсии:
```
p(i,i) = 1
p(n,1) = 1
p(n,k) = 0 при k > n
```

Для устранения экспоненциальной сложности рекурсии использовано
кэширование промежуточных результатов.

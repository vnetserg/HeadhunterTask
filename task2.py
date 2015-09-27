#!/usr/bin/python3.4

'''
    Файл с решением второй задачи.

    ЗАДАЧА: для данных натуральных чисел n и k определите
    количество способов представить число n в виде суммы k
    натуральных слагаемых, если способы, отличающиеся только
    порядком слагаемых, считать одинаковыми. n <= 150, k <= 150

    ФОРМАТ ВХОДНЫХ ДАННЫХ:
    Программа получает на вход два целочисленных аргумента - числа
    n и k.

    ФОРМАТ ВЫХОДНЫХ ДАННЫХ:
    В стандартный вывод печатается целое число, являющееся ответом.

    Описание алгоритма решения приведено в README.
'''

import argparse

def num_fragments(n, k, cache=None):
    '''
        Вернуть число разбиений числа n на k слагаемых. Аргументы:
            n - целое число
            k - целое число
            cache - словарь, ключи в котором - пары (n,k),
                    значения - вычисленные зачения функции
                    с этими параметрами
    '''
    if n == k or k == 1:
        return 1
    if k > n:
        return 0
    if cache is None:
        cache = {}
    if (n,k) in cache:
        return cache[(n,k)]
    cache[(n,k)] = num_fragments(n-1, k-1, cache) + num_fragments(n-k, k, cache)
    return cache[(n,k)]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("n", help="the number to split", type=int)
    parser.add_argument("k", help="number of split fragments", type=int)
    args = parser.parse_args()
    print(num_fragments(args.n, args.k))

if __name__ == "__main__":
    main()
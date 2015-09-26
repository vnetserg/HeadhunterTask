#!/usr/bin/python3.4

import argparse

def num_fragments(n, k, cache=None):
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
def pow(x: int, y: int) -> int:
    if y == 0:
        return 1
    return x * pow(x, y - 1)


def fibb(n: int) -> int:
    if n == 0:
        return 0
    if n == 1:
        return 1
    return fibb(n - 1) + fibb(n - 2)


def inverse(x: float) -> float:
    return 1 / x


print(pow(2, 5))
print(fibb(14))
print(inverse(3.14))
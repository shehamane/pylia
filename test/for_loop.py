def main(y: int):
    x = [1, 2, (2 + 2 * 2)]

    for i in range(len(x)):
        x[i] += y
    print(x)


for i in range(10):
    main(i)

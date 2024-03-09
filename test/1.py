def relu(z):
    return np.maximum(0, z)


def binary_cross_entropy(y_true, y_pred):
    epsilon = 1e-15
    y_pred = np.maximum(epsilon, np.minimum(1 - epsilon, y_pred))
    return -np.mean(y_true * np.log(y_pred) + (1 - y_true) * np.log(1 - y_pred))


def accuracy(y_true, y_pred):
    return np.mean(np.equal(y_true, np.round(y_pred)))


def gradient_descent(X, y, learning_rate, num_iterations):
    m, n = np.shape(X)
    theta = np.zeros(n)

    for i in range(num_iterations):
        z = np.dot(X, theta)
        h = relu(z)
        gradient = np.dot(np.transpose(X), (h - y)) / m
        theta = theta - learning_rate * gradient

        if i % 100 == 0:
            loss = binary_cross_entropy(y, h)
            acc = accuracy(y, h)

    return theta
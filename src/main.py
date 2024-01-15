import os
import pickle

import numpy as np

DATASET_PATH = "cifar-10-batches-py"


def load_batch(filename):
    with open(os.path.join(DATASET_PATH, filename), "rb") as f:
        dic = pickle.load(f, encoding="bytes")

    X = np.reshape(dic[b"data"], (10000, 3072)).swapaxes(0, 1)
    X = X.astype(float)
    X /= 255.0
    X -= np.mean(X, axis=1).reshape(-1, 1)
    X /= np.std(X, axis=1).reshape(-1, 1)

    y = np.array(dic[b"labels"])
    K = np.max(y)
    Y = np.array(list(map(lambda k: [0] * k + [1] + [0] * (K - k), y))).swapaxes(0, 1)

    return X, Y


def load_all():
    Xs, Ys = [], []
    for i in range(1, 6):
        X, Y = load_batch(f"data_batch_{i}")
        Xs.append(X)
        Ys.append(Y)

    return np.concatenate(Xs, axis=1), np.concatenate(Ys, axis=1)


def accuracy(Y, P):
    return np.mean(np.argmax(P, axis=0) == np.argmax(Y, axis=0))


def split_train_test(X, Y, ratio=0.8):
    N = X.shape[1]
    N_train = int(N * ratio)

    return (
        X[:, :N_train],
        Y[:, :N_train],
        X[:, N_train:],
        Y[:, N_train:],
    )


if __name__ == "__main__":
    from .layer import DenseLayer, SoftMaxLayer
    from .network import Network

    X, Y = load_all()
    print(X.shape, Y.shape)
    X_train, Y_train, X_test, Y_test = split_train_test(X, Y)

    model = Network(
        [
            DenseLayer(3072, 50, 5e-3),
            SoftMaxLayer(),
            DenseLayer(50, 10, 5e-3),
            SoftMaxLayer(),
        ]
    )

    print(accuracy(Y_test, model.predict(X_test)))
    model.fit(X_train, Y_train)
    print(accuracy(Y_test, model.predict(X_test)))
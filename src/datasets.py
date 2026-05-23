"""Dataset loading utilities.

Downloads libsvm-format datasets and caches them locally.
"""
from __future__ import annotations
from pathlib import Path
import urllib.request
import bz2
import shutil
import numpy as np
from sklearn.datasets import load_svmlight_file

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DATA_DIR.mkdir(exist_ok=True)

URLS = {
    "a9a":       "https://www.csie.ntu.edu.tw/~cjlin/libsvmtools/datasets/binary/a9a",
    "a9a.t":     "https://www.csie.ntu.edu.tw/~cjlin/libsvmtools/datasets/binary/a9a.t",
    "mnist":     "https://www.csie.ntu.edu.tw/~cjlin/libsvmtools/datasets/multiclass/mnist.bz2",
    "mnist.t":   "https://www.csie.ntu.edu.tw/~cjlin/libsvmtools/datasets/multiclass/mnist.t.bz2",
    "ijcnn1":    "https://www.csie.ntu.edu.tw/~cjlin/libsvmtools/datasets/binary/ijcnn1.bz2",
    "ijcnn1.t":  "https://www.csie.ntu.edu.tw/~cjlin/libsvmtools/datasets/binary/ijcnn1.t.bz2",
}


def _download(name: str) -> Path:
    url = URLS[name]
    local = DATA_DIR / url.rsplit("/", 1)[1]
    if not local.exists():
        print(f"Downloading {url} -> {local}")
        urllib.request.urlretrieve(url, local)
    # decompress .bz2 transparently
    if local.suffix == ".bz2":
        out = local.with_suffix("")
        if not out.exists():
            with bz2.open(local, "rb") as fi, open(out, "wb") as fo:
                shutil.copyfileobj(fi, fo)
        return out
    return local


def load_a9a():
    """Binary classification, labels in {-1, +1}, 123 features."""
    Xtr, ytr = load_svmlight_file(str(_download("a9a")), n_features=123)
    Xte, yte = load_svmlight_file(str(_download("a9a.t")), n_features=123)
    return Xtr, ytr, Xte, yte


def load_mnist():
    """10-class digits, 784 features (pixels scaled to [0,1])."""
    Xtr, ytr = load_svmlight_file(str(_download("mnist")), n_features=780)
    Xte, yte = load_svmlight_file(str(_download("mnist.t")), n_features=780)
    return Xtr, ytr.astype(int), Xte, yte.astype(int)


def load_ijcnn1():
    Xtr, ytr = load_svmlight_file(str(_download("ijcnn1")), n_features=22)
    Xte, yte = load_svmlight_file(str(_download("ijcnn1.t")), n_features=22)
    return Xtr, ytr, Xte, yte

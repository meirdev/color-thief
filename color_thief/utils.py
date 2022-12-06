import cv2

from .algo import Counter, KMeans, Regular
from .types import RGB


def rgb_to_hex(rgb: RGB) -> str:
    return "#{0:02x}{1:02x}{2:02x}".format(*rgb)


def factory(path: str, algo: str, colors: int) -> Counter:
    match algo:
        case "kmeans[RGB]":
            algo = KMeans()
        case "kmeans[LAB]":
            algo = KMeans("LAB")
        case "regular":
            algo = Regular()

    return algo.run(cv2.imread(path, cv2.IMREAD_UNCHANGED), colors)

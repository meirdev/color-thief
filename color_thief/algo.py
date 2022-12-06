import abc
import collections
from typing import Literal, TypeAlias

import cv2
import numpy as np
from sklearn.cluster import MiniBatchKMeans

from .libs import octree_quantizer
from .types import RGB

Counter: TypeAlias = dict[RGB, int]


def counter(unique_result: tuple[np.ndarray, np.ndarray], limit: int) -> Counter:
    values, counts = unique_result

    values = tuple(tuple(i) for i in values)
    counts = tuple(counts.tolist())

    return dict(
        list(sorted(zip(values, counts), key=lambda x: x[1], reverse=True))[:limit]
    )


class Algo(abc.ABC):
    @abc.abstractmethod
    def run(self, image: np.ndarray, colors: int) -> Counter:
        ...


class KMeans(Algo):
    def __init__(self, color_space: Literal["RGB", "LAB"] = "RGB") -> None:
        if color_space == "LAB":
            convert = (cv2.COLOR_BGR2LAB, cv2.COLOR_LAB2RGB)
        else:
            convert = (cv2.COLOR_BGR2RGB, None)

        self._convert = convert

    def run(self, image: np.ndarray, colors: int) -> Counter:
        image = cv2.cvtColor(image, self._convert[0])
        image = image.reshape((image.shape[0] * image.shape[1], 3))

        clt = MiniBatchKMeans(n_clusters=colors, random_state=0)
        labels = clt.fit_predict(image)
        quant = clt.cluster_centers_.astype("uint8")[labels]
        values, counts = np.unique(quant, return_counts=True, axis=0)

        if self._convert[1]:
            values = values.reshape((1, *values.shape))
            values = cv2.cvtColor(values, self._convert[1])
            values = values.reshape(*values.shape[1:])

        return counter((values, counts), colors)


class Regular(Algo):
    def run(self, image: np.ndarray, colors: int) -> Counter:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = image.reshape((image.shape[0] * image.shape[1], 3))

        unique_result = np.unique(image, return_counts=True, axis=0)

        return counter(unique_result, colors)


class Octree(Algo):
    def run(self, image: np.ndarray, colors: int) -> Counter:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        octree = octree_quantizer.OctreeQuantizer()

        for h in range(image.shape[1]):
            for w in range(image.shape[0]):
                octree.add_color(octree_quantizer.Color(*image[w, h]))

        palette = octree.make_palette(256)

        counter = collections.Counter()

        for h in range(image.shape[1]):
            for w in range(image.shape[0]):
                index = octree.get_palette_index(octree_quantizer.Color(*image[w, h]))
                color = palette[index]
                counter[(color.red, color.green, color.blue)] += 1

        return dict(counter.most_common(colors))


class MedianCut(Algo):
    def run(self, image: np.ndarray, colors: int) -> Counter:
        pass

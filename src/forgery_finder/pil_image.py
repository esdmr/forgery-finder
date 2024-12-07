from pathlib import Path
from typing import IO
import PIL.Image as img
from PIL.Image import Image
import cv2 as cv
import cv2.typing as cvt
import numpy as np


def from_cv(i: cvt.MatLike) -> Image:
    """
    Source: https://stackoverflow.com/a/65634189
    """
    rgb = cv.cvtColor(i, cv.COLOR_BGR2RGB)
    return img.fromarray(rgb)  # type: ignore


def to_cv(i: Image) -> cvt.MatLike:
    """
    Source: https://stackoverflow.com/a/65634189
    """
    return cv.cvtColor(np.array(i), cv.COLOR_RGB2BGR)


def open(fp: str | Path | IO[bytes]) -> Image:
    return img.open(fp)  # type: ignore


def resize(i: Image, size: tuple[int, int]) -> Image:
    return i.resize(size)  # type: ignore


def convert(i: Image, mode: str) -> Image:
    return i.convert(mode)  # type: ignore


def save(i: Image, fp: str | Path) -> None:
    i.save(fp)  # type: ignore

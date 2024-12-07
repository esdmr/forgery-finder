from typing import Iterable
from .skimage import structural_similarity
from . import imutils as imu
from . import pil_image as img
import cv2 as cv
import cv2.typing as cvt
import numpy as np
import numpy.typing as npt

UNIFORM_SIZE = (250, 160)
CONTOUR_RECTANGLE_COLOR_BGR = (0, 0, 255)

def make_uniform(i: img.Image) -> img.Image:
    return img.convert(img.resize(i, UNIFORM_SIZE), "RGB")


def to_grayscale(i: cvt.MatLike) -> cvt.MatLike:
    return cv.cvtColor(i, cv.COLOR_BGR2GRAY)


def get_structural_similarity(
    original_gray: cvt.MatLike,
    uploaded_gray: cvt.MatLike,
) -> tuple[float, npt.NDArray[np.uint8]]:
    score, diff = structural_similarity(original_gray, uploaded_gray)
    return score, (abs(diff) * 255).astype(np.uint8)


def get_threshold(diff: cvt.MatLike) -> cvt.MatLike:
    return cv.threshold(diff, 0, 255, cv.THRESH_BINARY_INV | cv.THRESH_OTSU)[1]


def get_contours(threshold: cvt.MatLike) -> Iterable[cvt.MatLike]:
    return imu.grab_contours(
        cv.findContours(threshold, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    )


def draw_contours_on_image(contours: Iterable[cvt.MatLike], image: cvt.MatLike) -> None:
    for i in contours:
        (x, y, w, h) = cv.boundingRect(i)
        cv.rectangle(image, (x, y), (x + w, y + h), CONTOUR_RECTANGLE_COLOR_BGR, 2)


class VerificationResult:
    def __init__(
        self,
        *,
        score: float,
        uploaded: cvt.MatLike,
        original: cvt.MatLike,
        diff: cvt.MatLike,
        threshold: cvt.MatLike,
    ) -> None:
        self.score = score
        self.uploaded = uploaded
        self.original = original
        self.diff = diff
        self.threshold = threshold


def verify(
    uploaded_image_pil: img.Image, original_image_pil: img.Image
) -> VerificationResult:
    uploaded_image = img.to_cv(make_uniform(uploaded_image_pil))
    original_image = img.to_cv(make_uniform(original_image_pil))

    uploaded_gray = to_grayscale(uploaded_image)
    original_gray = to_grayscale(original_image)

    score, diff = get_structural_similarity(original_gray, uploaded_gray)

    threshold = get_threshold(diff)
    contours = get_contours(threshold)

    draw_contours_on_image(contours, uploaded_image)
    draw_contours_on_image(contours, original_image)

    return VerificationResult(
        score=score,
        uploaded=uploaded_image,
        original=original_image,
        diff=diff,
        threshold=threshold,
    )

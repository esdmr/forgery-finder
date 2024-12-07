from typing import Any, Iterable
import imutils as imu
import cv2.typing as cvt


def grab_contours(contours: Any) -> Iterable[cvt.MatLike]:
    return imu.grab_contours(contours)  # type: ignore

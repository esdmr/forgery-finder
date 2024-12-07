import skimage.metrics as skim
import cv2.typing as cvt
import numpy as np
import numpy.typing as npt


def structural_similarity(
    a: cvt.MatLike,
    b: cvt.MatLike,
) -> tuple[float, npt.NDArray[np.float64]]:
    return skim.structural_similarity(a, b, full=True)  # type: ignore

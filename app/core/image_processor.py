import cv2
import numpy as np
from PyQt5.QtGui import QImage


class ImageProcessor:
    """
    Handles image loading, resizing, conversion (CV to Qt), and brightness/contrast adjustments.
    """

    def __init__(self):
        self._brightness = [0] * 4
        self._contrast = [1.0] * 4
        self._min_width = None
        self._min_height = None

    # --- Properties ---
    @property
    def min_width(self):
        return self._min_width

    @property
    def min_height(self):
        return self._min_height

    # --- Core Methods ---

    def process_input_images(self, images):
        """
        Calculates the minimum size, resizes, and applies brightness/contrast to all loaded images.
        Returns a list of processed grayscale images ready for FFT.
        """
        valid_images = [img for img in images if img is not None]
        if not valid_images:
            return [None] * 4

        # 1. Unify Sizing
        self._min_height = min(image.shape[0] for image in valid_images)
        self._min_width = min(image.shape[1] for image in valid_images)

        processed_images = []
        for idx, image in enumerate(images):
            if image is not None:
                # 2. Adjust Brightness and Contrast
                adjusted_image = cv2.convertScaleAbs(image,
                                                     alpha=self._contrast[idx],
                                                     beta=self._brightness[idx])

                # 3. Resize to minimum dimensions
                resized_image = cv2.resize(adjusted_image, (self._min_width, self._min_height),
                                           interpolation=cv2.INTER_LINEAR)

                processed_images.append(resized_image)
            else:
                processed_images.append(None)

        return processed_images

    def convert_cv_to_qt(self, cv_image: np.ndarray) -> QImage | None:
        """Converts an OpenCV image (np.ndarray) to a QImage for PyQt display."""
        if cv_image is None:
            return None

        if cv_image.ndim == 2:  # Grayscale
            height, width = cv_image.shape
            bytes_per_line = width
            return QImage(cv_image.data.tobytes(), width, height, bytes_per_line, QImage.Format_Grayscale8)

        elif cv_image.ndim == 3 and cv_image.shape[2] == 3:  # Color (BGR -> RGB)
            # OpenCV loads as BGR, QImage expects RGB for Format_RGB888
            rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
            height, width, channel = rgb_image.shape
            bytes_per_line = channel * width
            return QImage(rgb_image.data.tobytes(), width, height, bytes_per_line, QImage.Format_RGB888)

        return None

    # --- Adjustment Control Methods ---

    def set_brightness(self, index, value):
        self._brightness[index] = value

    def set_contrast(self, index, value):
        # Ensure contrast is non-negative
        self._contrast[index] = max(0.0, value)

    def reset_adjustments(self, index):
        self._brightness[index] = 0
        self._contrast[index] = 1.0
import numpy as np
import cv2


class FFTAnalyzer:
    """
    Handles Fourier Transform computations, component extraction, and region selection logic.
    """

    def __init__(self, image_processor):
        self.image_processor = image_processor
        self.ft_images = [None] * 4  # Stores the visual FT component (Magnitude, Phase, etc.)
        self.selector_region = [0, 0, 200, 200]  # [x, y, width, height]
        self.ft_mode = "Magnitude / Phase"

    # --- Core Methods ---

    def compute_ft_components(self, images, component_selections):
        """
        Computes and stores the visual FT component for all images.
        Returns a list of the 4 FT component images (normalized uint8 or color).
        """
        min_h = self.image_processor.min_height
        min_w = self.image_processor.min_width

        for i, image in enumerate(images):
            if image is None or min_h is None or min_w is None:
                self.ft_images[i] = None
                continue

            ft_image = np.fft.fft2(image)
            ft_image_shifted = np.fft.fftshift(ft_image)

            selected = component_selections[i]

            if selected == "FT Magnitude":
                magnitude = np.abs(ft_image_shifted)
                # Apply log scaling and normalize for display
                magnitude_log = np.log1p(magnitude)
                ft_visual = cv2.normalize(magnitude_log, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

                # Magnitude uses TURBO (high contrast)
                ft_visual = cv2.applyColorMap(ft_visual, cv2.COLORMAP_TURBO)

            elif selected == "FT Phase":
                phase = np.angle(ft_image_shifted)
                # Scale phase to [0, 255]
                phase_scaled = (phase + np.pi) / (2 * np.pi) * 255
                ft_visual = phase_scaled.astype(np.uint8)

                # Phase uses JET
                ft_visual = cv2.applyColorMap(ft_visual, cv2.COLORMAP_JET)


            elif selected == "FT Real":
                real = np.real(ft_image_shifted)
                real_log = np.log1p(np.abs(real))
                ft_visual = cv2.normalize(real_log, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

                # THEME CHANGE: Real uses RAINBOW for better differentiation
                ft_visual = cv2.applyColorMap(ft_visual, cv2.COLORMAP_RAINBOW)


            elif selected == "FT Imaginary":
                imaginary = np.imag(ft_image_shifted)
                imaginary_log = np.log1p(np.abs(imaginary))
                ft_visual = cv2.normalize(imaginary_log, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

                # THEME CHANGE: Imaginary uses VIRIDIS for distinct color mapping
                ft_visual = cv2.applyColorMap(ft_visual, cv2.COLORMAP_VIRIDIS)

            else:
                ft_visual = None

            self.ft_images[i] = ft_visual

        return self.ft_images

    # --- Selector Methods ---

    def set_region_size(self, size):
        """Sets the width and height of the selector region (centered)."""
        if self.image_processor.min_height is None or self.image_processor.min_width is None:
            return False

        rect_size = max(50, size)
        self.selector_region[2] = rect_size  # Width
        self.selector_region[3] = rect_size  # Height

        # Center the selector on the image
        height = self.image_processor.min_height
        width = self.image_processor.min_width
        x = (width - rect_size) // 2
        y = (height - rect_size) // 2
        self.selector_region[0] = x
        self.selector_region[1] = y

        return True

    def get_component_options(self):
        """Returns the options for the component combo boxes based on the current mode."""
        if self.ft_mode == "Magnitude / Phase":
            return ["FT Magnitude", "FT Phase"]
        elif self.ft_mode == "Real / Imaginary":
            return ["FT Real", "FT Imaginary"]
        return []

    def set_ft_mode(self, mode):
        self.ft_mode = mode

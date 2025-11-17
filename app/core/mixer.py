import numpy as np
import cv2


class Mixer:
    """
    Handles the complex Fourier Transform mixing process and mask application.
    Decoupled from UI display logic.
    """

    def __init__(self):
        self._region_mode = "None"
        self._output_label_1 = None
        self._output_label_2 = None
        # Removed _output_selector as it's no longer necessary

    # --- Properties ---
    @property
    def region_mode(self):
        return self._region_mode

    def set_region_mode(self, mode):
        # Map segmented control text to internal mode
        if "Inner" in mode:
            self._region_mode = "Inner"
        elif "Outer" in mode:
            self._region_mode = "Outer"
        else:
            self._region_mode = "None"

    def set_output_labels(self, label1, label2):
        """
        Set references to UI output image elements.
        The selector reference is now handled solely in ApplicationLogic.
        """
        self._output_label_1 = label1
        self._output_label_2 = label2

    # --- Core Methods ---

    def mix_images(self, images, weights, component_selections, selector_region, min_height, min_width):
        """Mixes images based on selected components, weights, and region mode."""
        if min_width is None or min_height is None:
            return np.zeros((100, 100), dtype=np.uint8)

        # Initialize complex FT array
        combined_ft = np.zeros((min_height, min_width), dtype=np.complex128)

        for i in range(4):
            if images[i] is None or weights[i] == 0.0:
                continue

            weight = weights[i]
            ft_image = np.fft.fft2(images[i])
            ft_image_shifted = np.fft.fftshift(ft_image)

            # 1. Apply Region Mask
            ft_image_masked = self.__apply_region_mask(ft_image_shifted, selector_region, min_height, min_width)

            # 2. Extract and Weight Component
            selected = component_selections[i]

            if selected in ["FT Magnitude", "FT Phase"]:
                # Magnitude/Phase mixing relies on combining weighted complex numbers
                magnitude = np.abs(ft_image_masked)
                phase = np.angle(ft_image_masked)

                if selected == "FT Magnitude":
                    # Weight the contribution of the full complex number
                    weighted_complex = weight * magnitude * np.exp(1j * phase)

                elif selected == "FT Phase":
                    # Use weighted phase information, maintaining original magnitude scale (1)
                    weighted_complex = weight * np.exp(1j * phase)

                combined_ft += weighted_complex

            elif selected in ["FT Real", "FT Imaginary"]:
                # Real/Imaginary mixing combines the complex parts directly

                real_part = np.real(ft_image_masked)
                imag_part = np.imag(ft_image_masked)

                if selected == "FT Real":
                    combined_ft += weight * (real_part + 0j)
                elif selected == "FT Imaginary":
                    combined_ft += weight * (0 + 1j * imag_part)

        # 3. Inverse Fourier Transform
        combined_ft_shifted = np.fft.ifftshift(combined_ft)
        mixed_image_complex = np.fft.ifft2(combined_ft_shifted)

        # Take magnitude for the final output image
        mixed_image = np.abs(mixed_image_complex)

        # 4. Normalize and return
        mixed_image_normalized = cv2.normalize(mixed_image, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        return mixed_image_normalized

    def __apply_region_mask(self, ft_data, selector_region, height, width):
        """Apply a mask based on region mode (Inner, Outer, None)."""
        mask = np.ones_like(ft_data, dtype=np.float64)

        # Region dimensions
        x, y, w, h = selector_region

        # Clamp region to image bounds
        x = max(0, min(x, width - w))
        y = max(0, min(y, height - h))

        if self._region_mode == "Inner":
            # Mask is 1 inside the box (low frequencies/center), 0 outside
            mask[:, :] = 0.0
            mask[y:y + h, x:x + w] = 1.0

        elif self._region_mode == "Outer":
            # Mask is 0 inside the box, 1 outside (high frequencies)
            mask[y:y + h, x:x + w] = 0.0

        # If "None", mask remains all 1s (no masking)

        return ft_data * mask

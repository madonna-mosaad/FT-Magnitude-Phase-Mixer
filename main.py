import sys
import os
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QFileDialog, QMainWindow, QWidget, QLabel, QSizePolicy
from PyQt5.QtCore import QObject, Qt, pyqtSlot
from PyQt5.QtGui import QPixmap
from app.gui.main_window import MainWindow
from app.core.image_processor import ImageProcessor
from app.core.fft_analyzer import FFTAnalyzer
from app.core.mixer import Mixer
from app.workers.mixing_thread import MixingThread, MixingThreadSignals
from app.gui.ui_components import SegmentedControl  # Import SegmentedControl for dynamic updates


class ApplicationLogic(QObject):
    def __init__(self):
        super().__init__()
        # CORE INITIALIZATION
        self.image_processor = ImageProcessor()
        self.mixer = Mixer()
        self.fft_analyzer = FFTAnalyzer(self.image_processor)

        self.ui = None
        self.raw_images = [None] * 4  # Original grayscale images
        self.current_weights = [0.0] * 4
        self.active_image_index = None

        # THREADING SETUP
        self.worker_thread = None
        self.thread_signals = MixingThreadSignals()
        self.thread_signals.finished.connect(self.on_mixing_finished)
        self.thread_signals.progress.connect(self.on_mixing_progress)
        self.thread_signals.error.connect(self.on_mixing_error)
        self.thread_signals.canceled.connect(self.on_mixing_canceled)

    def set_ui(self, ui_instance):
        """Initializes UI references and default state."""
        self.ui = ui_instance
        self.mixer.set_output_labels(self.ui.output_image_1, self.ui.output_image_2)

        # Initial component setup based on default SegmentedControl selection
        if hasattr(self.ui.ft_mode_selector, 'get_selection'):
            self.handle_ft_mode_change(self.ui.ft_mode_selector.get_selection())

        if hasattr(self.ui.region_mode_selector, 'get_selection'):
            self.mixer.set_region_mode(self.ui.region_mode_selector.get_selection())

        # Connect the 'Save Mixed Output' button
        self.ui.cancel_button.clicked.connect(self.save_mixed_image)

    @pyqtSlot()
    def cleanup_on_exit(self):
        """Ensures the worker thread is terminated when the application closes."""
        if self.worker_thread and self.worker_thread.is_alive():
            print("Cleaning up active worker thread...")
            self.worker_thread.cancel()

    # --- Worker Thread Methods ---

    def start_mixing_process(self):
        """Prepares and starts the background mixing thread."""

        # If thread is alive, cancel the current job (non-blocking call)
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.cancel()

        # Input Validation (Robust check)
        can_mix = False
        # UPDATED: Use get_selection() on the new component selectors
        component_selections = [selector.get_selection() for selector in self.ui.component_selectors]

        # Check if any images are loaded AT ALL
        if not any(img is not None for img in self.raw_images):
            self.ui.status_label.setText("Load at least one image.")
            return

        for i in range(4):
            if self.raw_images[i] is not None and self.current_weights[i] > 0.0:
                # Note: SegmentedControl always has a selection, so checking for "Select Component" might not be strictly needed,
                # but we rely on the component list being valid (set in handle_ft_mode_change)
                if component_selections[i] in ["Select Mode"]:
                    self.ui.status_label.setText(f"Error: Select a component for Viewport {i + 1}")
                    return
                can_mix = True

        if not can_mix:
            self.ui.status_label.setText("Set non-zero weights for loaded images.")
            # Clear output if no mixing is possible (e.g., all weights are zero)
            self.clear_mixed_output()
            return

        self.ui.status_label.setText("Mixing...")
        self.ui.progress_bar.setValue(0)

        # Always create a new thread instance for a new job
        self.worker_thread = MixingThread(self, self.thread_signals)
        self.worker_thread.start()

    def execute_mixing_core(self):
        """
        [Called by the worker thread] Executes the heavy-lifting FFT and mixing logic.
        """
        # 1. Get current parameters
        processed_images = self.image_processor.process_input_images(self.raw_images)
        # UPDATED: Use get_selection() on the new component selectors
        component_selections = [selector.get_selection() for selector in self.ui.component_selectors]
        min_h = self.image_processor.min_height
        min_w = self.image_processor.min_width

        # 2. Mix
        mixed_image = self.mixer.mix_images(
            images=processed_images,
            weights=self.current_weights,
            component_selections=component_selections,
            selector_region=self.fft_analyzer.selector_region,
            min_height=min_h,
            min_width=min_w
        )
        return mixed_image

    @pyqtSlot(object)
    def on_mixing_finished(self, mixed_image: np.ndarray):
        """Handles the resulting image from the worker thread."""
        qt_image = self.image_processor.convert_cv_to_qt(mixed_image)
        if qt_image:
            pixmap = QPixmap.fromImage(qt_image)
            target_label = self.ui.output_image_1 if self.ui.output_selector.get_selection() == "Output 1" else self.ui.output_image_2
            target_label.setPixmap(pixmap.scaled(target_label.size(), Qt.KeepAspectRatio))
            self.ui.status_label.setText("Mixing Complete")

    @pyqtSlot(int)
    def on_mixing_progress(self, value):
        self.ui.progress_bar.setValue(value)

    @pyqtSlot(str)
    def on_mixing_error(self, message):
        # We now expect to land here instead of crashing the process
        self.ui.status_label.setText(f"Error: {message}")
        print(f"THREAD EXCEPTION CAUGHT: {message}")
        self.clear_mixed_output()  # Clear output on error

    @pyqtSlot()
    def on_mixing_canceled(self):
        self.ui.status_label.setText("Mixing Canceled")
        self.ui.progress_bar.setValue(0)
        self.clear_mixed_output()  # Clear output on cancel

    def clear_mixed_output(self):
        """Clears both output image labels."""
        self.ui.output_image_1.clear()
        self.ui.output_image_2.clear()
        self.ui.output_image_1.setText("Mixed Image 1")
        self.ui.output_image_2.setText("Mixed Image 2")

    # --- Save Mixed Output ---
    @pyqtSlot()
    def save_mixed_image(self):
        """Saves the image from the currently selected output viewport."""

        # Determine which output label to save from
        selected_output = self.ui.output_selector.get_selection()
        target_label = self.ui.output_image_1 if selected_output == "Output 1" else self.ui.output_image_2

        pixmap = target_label.pixmap()

        # Check if the output widget is empty (contains no image)
        if pixmap is None or pixmap.isNull():
            self.ui.status_label.setText("Error: The selected output is empty. Nothing to save.")
            return

        options = QFileDialog.Options()

        default_filename = "mixed_image.png"
        initial_path = os.path.join("/", default_filename)

        file_name, _ = QFileDialog.getSaveFileName(self.ui, "Save Mixed Image", initial_path,
                                                   "PNG Files (*.png);;JPEG Files (*.jpg *.jpeg);;All Files (*)", options=options)

        if file_name:
            if pixmap.save(file_name):
                self.ui.status_label.setText(f"Output saved to: {os.path.basename(file_name)}")
            else:
                self.ui.status_label.setText("Error: Could not save the image file.")

    def cancel_mixing(self):
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.cancel()
        else:
            self.ui.status_label.setText("No active mixing job.")

    # --- Input & Adjustment Methods ---

    def load_image(self, index):
        """Loads an image, converts to grayscale, and updates state."""
        options = QFileDialog.Options()
        search_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'images')
        file_name, _ = QFileDialog.getOpenFileName(self.ui, "Open Grayscale Image", search_path,
                                                   "Images (*.png *.jpg *.jpeg *.bmp);;All Files (*)", options=options)
        if file_name:
            image = cv2.imread(file_name)
            if image is not None:
                gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                self.raw_images[index] = gray_image

                self.reset_brightness_contrast(index, trigger_update=False)

                # This is handled naturally because load_image calls full_update_cycle()
                self.full_update_cycle()
            else:
                self.ui.status_label.setText("Error: Could not read the image file.")

    @pyqtSlot(int)
    def clear_image(self, index):
        """
        Clears the image and its data from a specific viewport.
        Handles checking if all images are cleared afterwards.
        """
        # Clear data for the specific index
        self.raw_images[index] = None
        self.current_weights[index] = 0.0
        self.image_processor.reset_adjustments(index)

        # Reset UI controls
        self.ui.weight_sliders[index].setValue(0)

        # Manually clear viewport display and FT component view
        self.ui.input_labels[index].clear()
        self.ui.input_labels[index].setText("Click to Load Image")
        self.ui.ft_labels[index].clear()
        self.ui.ft_labels[index].setText("FT Component View")

        # Clear output if all images are now cleared
        if not any(img is not None for img in self.raw_images):
            self.clear_mixed_output()
            self.ui.status_label.setText("All viewports cleared.")
            # Crucial: Reset min dimensions if no images are loaded
            self.image_processor._min_width = None
            self.image_processor._min_height = None
            self.update_ft_displays([None] * 4)  # Clear remaining FT displays
            return

        self.full_update_cycle()
        self.ui.status_label.setText(f"Viewport {index + 1} cleared.")

    @pyqtSlot(int, int)
    def update_weight(self, value, index):
        """Updates weight and triggers mixing."""
        self.current_weights[index] = value / 100.0

        self.full_update_cycle()

    @pyqtSlot(int, bool)
    def reset_brightness_contrast(self, index, trigger_update=True):
        """Resets B/C for one image."""
        self.image_processor.reset_adjustments(index)

        if trigger_update:
            self.full_update_cycle(trigger_mixing=False)

    def mouse_press_event(self, event, index):
        """Stores initial mouse position."""
        self.active_image_index = index
        self.last_mouse_y = event.y()
        self.last_mouse_x = event.x()

    def mouse_move_event(self, event, index):
        """Adjusts B/C on mouse drag."""
        if self.active_image_index == index and event.buttons() == Qt.LeftButton:
            dy = event.y() - self.last_mouse_y
            dx = event.x() - self.last_mouse_x

            # Brightness (vertical drag) and Contrast (horizontal drag)
            new_b = self.image_processor._brightness[index] + dy
            new_c = self.image_processor._contrast[index] + dx * 0.01

            self.image_processor.set_brightness(index, new_b)
            self.image_processor.set_contrast(index, new_c)

            self.last_mouse_y = event.y()
            self.last_mouse_x = event.x()

            self.full_update_cycle(trigger_mixing=False)

    # --- FT Component Handlers ---

    @pyqtSlot(str)
    def handle_ft_mode_change(self, selection):
        """Updates the component mode and populates segmented controls."""
        self.fft_analyzer.set_ft_mode(selection)
        options = self.fft_analyzer.get_component_options()

        # --- UPDATED: Dynamically rebuild the SegmentedControl buttons ---
        # Note: We must destroy and recreate the controls to change their options
        for i, old_selector in enumerate(self.ui.component_selectors):
            # 1. Store layout and position info
            parent_layout = old_selector.parentWidget().layout()

            # Find the index of the old selector in the layout
            selector_index = parent_layout.indexOf(old_selector)

            # 2. Delete the old widget from the layout
            parent_layout.removeWidget(old_selector)
            old_selector.deleteLater()

            # 3. Create the new segmented control with updated options
            new_selector = SegmentedControl(options)
            # Use Expanding policy now that it's the dominant item in its grid row/column
            new_selector.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

            # 4. Insert the new selector back into the layout at the same position
            parent_layout.insertWidget(selector_index, new_selector)

            # 5. Update the reference list in the UI instance
            self.ui.component_selectors[i] = new_selector

            # 6. Reconnect the signal
            new_selector.selection_changed.connect(self.handle_component_selection)
        # --- END UPDATED LOGIC ---

        self.full_update_cycle()

    @pyqtSlot(str)
    def handle_region_mode_change(self, selection):
        """Updates the region mask type (Inner, Outer, None)."""
        self.mixer.set_region_mode(selection)
        self.full_update_cycle()

    @pyqtSlot(int)
    def handle_region_size_change(self, value):
        """Updates the region size and triggers redraw."""
        # Check if images are loaded before resizing the selector region
        if any(img is not None for img in self.raw_images):
            if self.fft_analyzer.set_region_size(value):
                self.full_update_cycle(trigger_mixing=False)
        else:
            self.ui.status_label.setText("Load an image before changing region size.")

    @pyqtSlot(str)  # Now receives the text selection from SegmentedControl
    def handle_component_selection(self, selection):
        """A component selector was changed, trigger full update."""
        # The selection argument is the component name (e.g., "FT Magnitude")
        self.full_update_cycle()

    # --- Unified Update Logic ---

    def full_update_cycle(self, trigger_mixing=True):
        """Performs image processing, FT calculation, and optional mixing."""

        # Check if the list contains any images (i.e., elements that are not None).
        if not any(img is not None for img in self.raw_images):
            # No images loaded. Only clear FT views, do not proceed to math.
            self.update_ft_displays([None] * 4)
            self.image_processor._min_width = None
            self.image_processor._min_height = None
            return

        # 1. Process Images (B/C, Resize, Unify)
        processed_images = self.image_processor.process_input_images(self.raw_images)

        # --- FIX: Ensure the selector region is centered after image dimensions are set ---
        if self.image_processor.min_width is not None and self.ui is not None:
            region_x, region_y, _, _ = self.fft_analyzer.selector_region
            if region_x == 0 and region_y == 0:
                default_size = self.ui.region_size_slider.value()
                self.fft_analyzer.set_region_size(default_size)
        # ---------------------------------------------------------------------------------

        # 2. Update Input Image Displays
        self.update_input_displays(processed_images)

        # 3. Compute and Update FT Displays
        # UPDATED: Use get_selection() on the new component selectors
        component_selections = [selector.get_selection() for selector in self.ui.component_selectors]
        ft_visuals = self.fft_analyzer.compute_ft_components(processed_images, component_selections)
        self.update_ft_displays(ft_visuals)

        # 4. Trigger Mixing (on a thread)
        if trigger_mixing:
            self.start_mixing_process()

    # --- Display Update Helpers (update_input_displays, update_ft_displays, __draw_selector_on_ft_image remain the same) ---

    def update_input_displays(self, processed_images):
        """Updates the input image labels."""
        for i, image in enumerate(processed_images):
            label = self.ui.input_labels[i]

            # Since the user requested it removed, we use the static text unless the image is loaded/being manipulated
            if image is not None:
                # When image is loaded/being dragged, show current stats for feedback
                # self.ui.reset_buttons[i].setText(f"Reset (B:{b:.0f} | C:{c:.2f})")
                qt_image = self.image_processor.convert_cv_to_qt(image)
                if qt_image:
                    pixmap = QPixmap.fromImage(qt_image)
                    label.setPixmap(pixmap.scaled(label.size(), Qt.KeepAspectRatio))
            else:
                label.clear()
                label.setText("Click to Load Image")
                # self.ui.reset_buttons[i].setText("Reset")  # Static text when empty or reset

    def update_ft_displays(self, ft_visuals):
        """Updates the FT component labels, including the region selector overlay."""
        for i, ft_image in enumerate(ft_visuals):
            label = self.ui.ft_labels[i]
            if ft_image is not None:
                # Draw the selector on the visual image before converting to Qt
                ft_image_with_selector = self.__draw_selector_on_ft_image(ft_image)
                qt_image = self.image_processor.convert_cv_to_qt(ft_image_with_selector)
                if qt_image:
                    pixmap = QPixmap.fromImage(qt_image)
                    label.setPixmap(pixmap.scaled(label.size(), Qt.KeepAspectRatio))
            else:
                label.clear()
                label.setText("FT Component View")

    def __draw_selector_on_ft_image(self, ft_image):
        """Draws the semi-transparent region selector on the FT visual image."""
        if self.mixer.region_mode == "None":
            return ft_image

        ft_image_copy = ft_image.copy()
        x, y, w, h = self.fft_analyzer.selector_region

        if w == 0 or h == 0 or ft_image.ndim != 3:
            return ft_image

        # Create overlay
        overlay = ft_image_copy.copy()
        alpha = 0.4
        color = (0, 0, 255)  # BGR color for Red

        # Draw a solid rectangle on the overlay
        cv2.rectangle(overlay, (x, y), (x + w, y + h), color, -1)

        # Blend the overlay with the original image
        cv2.addWeighted(overlay, alpha, ft_image_copy, 1 - alpha, 0, ft_image_copy)

        # Draw the border
        cv2.rectangle(ft_image_copy, (x, y), (x + w, y + h), color, 2)

        return ft_image_copy


def main():
    app = QApplication(sys.argv)

    # Load and apply modern dark theme
    style_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'styles', 'dark_theme.qss')
    try:
        with open(style_path, 'r') as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print(f"Warning: Could not find theme file at {style_path}. Running with default style.")

    # Initialize Logic and UI
    app_logic = ApplicationLogic()
    main_window = MainWindow(app_logic)
    app_logic.set_ui(main_window)

    main_window.showFullScreen()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

from PyQt5.QtWidgets import QMainWindow, QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QComboBox, QPushButton, QProgressBar, QGroupBox, \
    QButtonGroup, QToolButton, QSizePolicy
from PyQt5.QtCore import Qt
from app.gui.ui_components import SegmentedControl


class MainWindow(QMainWindow):
    def __init__(self, app_logic):
        super().__init__()
        self.app_logic = app_logic  # Reference to the logic/core layer
        self.setWindowTitle("FT Image Mixer Pro")
        self.setGeometry(100, 100, 1400, 800)
        self.setMinimumSize(1200, 700)

        # NOTE: These initial values will be immediately overwritten by update_responsive_metrics()
        # but we define them to keep the original fields present exactly as in your version.
        self.INPUT_LABEL_WIDTH = 300
        self.FT_LABEL_WIDTH = 200
        self.VIEWPORT_HEIGHT = 280  # Fixed height for stability

        # Main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)

        self.setup_main_interface()
        self.setup_control_panel()
        self.connect_signals()

        # Ensure we set sizes responsively right after building widgets
        # Use the current window size as the basis for percentage calculations
        self.update_responsive_metrics(self.width(), self.height())

        # Connect QMainWindow's close event to the cleanup logic
        self.closeEvent = self.handle_close_event

    def handle_close_event(self, event):
        """Intercepts the close event to ensure threads are shut down."""
        self.app_logic.cleanup_on_exit()
        event.accept()

    # -------------------------
    # Responsive functions
    # -------------------------
    def update_responsive_metrics(self, window_w, window_h):
        """
        Robust responsive recalculation that prevents overlap by:
          - computing per-viewport available width (accounts for right control panel),
          - setting sensible min/max widths for input and FT labels,
          - switching the image area to vertical stacking when viewport is too narrow.
        This replaces brittle fixed-size logic with adaptive constraints.
        """

        # --- Configurable thresholds and ratios ---
        MIN_VIEWPORT_WIDTH = 300  # below this, stack vertically
        MIN_INPUT_WIDTH = 100
        MIN_FT_WIDTH = 80
        INPUT_RATIO = 0.62  # proportion of viewport width for input label
        FT_RATIO = 0.38  # proportion for FT label
        VIEWPORT_HEIGHT_RATIO = 0.26  # proportion of window height for viewport height
        MIN_VIEWPORT_HEIGHT = 120

        # --- Compute right-side control panel width if available, else guess using layout stretch ---
        right_panel_w = 0
        try:
            if hasattr(self, "control_panel") and self.control_panel is not None:
                right_panel_w = self.control_panel.width()
            else:
                # fallback: main_layout uses stretch (image_grid_widget, control_panel) ~ (3,1)
                right_panel_w = int(window_w * 0.25)
        except Exception:
            right_panel_w = int(window_w * 0.25)

        # --- Available width per viewport (two columns in the grid) ---
        # subtract margins and spacing conservatively
        total_margin_padding = 60  # conservative buffer for margins, groupbox padding, spacing
        available_for_grid = max(200, window_w - right_panel_w - total_margin_padding)
        per_viewport_w = max(160, int(available_for_grid / 2))

        # --- Compute desired pixel sizes ---
        desired_input_w = max(MIN_INPUT_WIDTH, int(per_viewport_w * INPUT_RATIO))
        desired_ft_w = max(MIN_FT_WIDTH, int(per_viewport_w * FT_RATIO))
        desired_viewport_h = max(MIN_VIEWPORT_HEIGHT, int(window_h * VIEWPORT_HEIGHT_RATIO))

        # Helper: replace the first child layout of a groupbox (image area) with a new layout (H or V)
        def _ensure_image_area_layout(viewport_group, input_widget, ft_widget, vertical=False):
            """
            Ensure the first layout inside viewport_group.layout() is either horizontal or vertical
            containing input_widget and ft_widget in that order.
            """
            parent_layout = viewport_group.layout()
            if parent_layout is None:
                return

            # Get the first item (expected to be the image row/layout)
            first_item = parent_layout.itemAt(0)
            existing_layout = None
            if first_item is not None:
                existing_layout = first_item.layout()  # may be None if a widget was placed directly

            # Check if existing layout already matches requested orientation
            if existing_layout is not None:
                is_horiz = isinstance(existing_layout, QHBoxLayout)
                is_vert = isinstance(existing_layout, QVBoxLayout)
                if (vertical and is_vert) or (not vertical and is_horiz):
                    # layout orientation already correct; ensure widgets are in place
                    # remove all items from layout and re-add input and ft widgets to guarantee order
                    while existing_layout.count():
                        itm = existing_layout.takeAt(0)
                        w = itm.widget()
                        if w is not None:
                            existing_layout.removeWidget(w)
                    if vertical:
                        existing_layout.addWidget(input_widget)
                        existing_layout.addWidget(ft_widget)
                    else:
                        existing_layout.addWidget(input_widget, 3)
                        existing_layout.addWidget(ft_widget, 2)
                    return

            # If we reach here, we need to replace the first item with a new layout
            # Remove and store remaining items of parent_layout temporarily
            remaining = []
            while parent_layout.count():
                itm = parent_layout.takeAt(0)
                remaining.append(itm)

            # Build new image layout
            if vertical:
                new_image_layout = QVBoxLayout()
                new_image_layout.setSpacing(8)
                new_image_layout.setContentsMargins(0, 0, 0, 0)
                new_image_layout.addWidget(input_widget)
                new_image_layout.addWidget(ft_widget)
            else:
                new_image_layout = QHBoxLayout()
                new_image_layout.setSpacing(10)
                new_image_layout.setContentsMargins(0, 0, 0, 0)
                new_image_layout.addWidget(input_widget, 3)
                new_image_layout.addWidget(ft_widget, 2)

            # Insert the new image layout as the first element of parent_layout
            parent_layout.addLayout(new_image_layout)

            # Re-append the remaining items (skip the old first item which we've removed)
            # Note: remaining[0] was the original first item; we've replaced it.
            for itm in remaining[1:]:
                # itm may be a layout item or widget item - re-add appropriately
                if itm.widget() is not None:
                    parent_layout.addWidget(itm.widget())
                elif itm.layout() is not None:
                    parent_layout.addLayout(itm.layout())

        # --- Iterate viewports and apply constraints & possible stacking ---
        try:
            count = len(getattr(self, "input_labels", []))
            for i in range(count):
                in_lbl = self.input_labels[i]
                ft_lbl = self.ft_labels[i]

                # Make labels flexible in policy
                try:
                    in_lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                    ft_lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                except Exception:
                    pass

                # If very narrow per-viewport width, stack vertically to avoid overlap
                if per_viewport_w < MIN_VIEWPORT_WIDTH:
                    # Give each label full width of viewport and modest height
                    in_lbl.setMaximumWidth(per_viewport_w)
                    ft_lbl.setMaximumWidth(per_viewport_w)
                    in_lbl.setMinimumWidth(80)
                    ft_lbl.setMinimumWidth(70)

                    in_lbl.setMinimumHeight(int(desired_viewport_h * 0.45))
                    ft_lbl.setMinimumHeight(int(desired_viewport_h * 0.45))

                    # Replace layout to vertical so FT sits below input
                    parent_group = in_lbl.parentWidget()
                    if isinstance(parent_group, QGroupBox):
                        _ensure_image_area_layout(parent_group, in_lbl, ft_lbl, vertical=True)
                else:
                    # Horizontal layout: assign proportional widths and reasonable heights
                    in_lbl.setMinimumWidth(MIN_INPUT_WIDTH)
                    ft_lbl.setMinimumWidth(MIN_FT_WIDTH)

                    in_lbl.setMaximumWidth(max(desired_input_w, MIN_INPUT_WIDTH))
                    ft_lbl.setMaximumWidth(max(desired_ft_w, MIN_FT_WIDTH))

                    in_lbl.setMinimumHeight(int(desired_viewport_h * 0.9))
                    ft_lbl.setMinimumHeight(int(desired_viewport_h * 0.9))

                    parent_group = in_lbl.parentWidget()
                    if isinstance(parent_group, QGroupBox):
                        _ensure_image_area_layout(parent_group, in_lbl, ft_lbl, vertical=False)
        except Exception:
            # If anything goes wrong, keep UI alive; avoid crash
            pass

        # --- Keep overall image grid height reasonable so bottom controls remain visible ---
        try:
            if hasattr(self, "image_grid_widget"):
                self.image_grid_widget.setMinimumHeight(min(int(window_h * 0.65), int(desired_viewport_h * 2.2)))
        except Exception:
            pass

        # --- Update outputs robustly (no overlap there) ---
        try:
            if hasattr(self, "output_image_1"):
                self.output_image_1.setMinimumSize(max(120, int(window_w * 0.10)), max(110, int(window_h * 0.12)))
            if hasattr(self, "output_image_2"):
                self.output_image_2.setMinimumSize(max(120, int(window_w * 0.10)), max(110, int(window_h * 0.12)))
        except Exception:
            pass

    def resizeEvent(self, event):
        """
        Recompute responsive metrics whenever the main window is resized.
        This uses the current widget width/height (not the screen) so the UI
        behaves like percent-of-window CSS.
        """
        new_w = self.width()
        new_h = self.height()
        self.update_responsive_metrics(new_w, new_h)
        super().resizeEvent(event)

    def setup_main_interface(self):
        # 2x2 Grid for Image Viewports
        self.image_grid_widget = QWidget()
        self.image_grid = QGridLayout(self.image_grid_widget)
        self.image_grid.setSpacing(10)

        # Store labels and controls for easy access
        self.input_labels = []
        self.ft_labels = []
        self.weight_sliders = []
        self.component_selectors = []
        self.reset_buttons = []
        self.clear_buttons = []

        for i in range(4):
            viewport_group = QGroupBox(f"Viewport {i + 1}")
            viewport_layout = QVBoxLayout()
            viewport_layout.setSpacing(10)
            viewport_layout.setContentsMargins(10, 10, 10, 10)
            viewport_group.setLayout(viewport_layout)

            # ---------- IMAGE ROW ----------
            image_row = QHBoxLayout()
            image_row.setSpacing(10)
            image_row.setContentsMargins(0, 0, 0, 0)

            # Input Image
            input_label = QLabel("Click to Load Image")
            input_label.setProperty("class", "input_image_label")
            input_label.setScaledContents(True)
            input_label.setAlignment(Qt.AlignCenter)
            input_label.setMinimumSize(self.INPUT_LABEL_WIDTH, self.VIEWPORT_HEIGHT)
            input_label.setMaximumSize(self.INPUT_LABEL_WIDTH * 2, self.VIEWPORT_HEIGHT * 2)
            self.input_labels.append(input_label)

            # FT Image
            ft_label = QLabel("FT Component View")
            ft_label.setProperty("class", "ft_component_label")
            ft_label.setScaledContents(True)
            ft_label.setAlignment(Qt.AlignCenter)
            ft_label.setMinimumSize(self.FT_LABEL_WIDTH, self.VIEWPORT_HEIGHT)
            ft_label.setMaximumSize(self.FT_LABEL_WIDTH * 2, self.VIEWPORT_HEIGHT * 2)
            self.ft_labels.append(ft_label)

            # Add images with fixed stretch ratios
            image_row.addWidget(input_label, 3)
            image_row.addWidget(ft_label, 2)

            viewport_layout.addLayout(image_row)

            # ---------- CONTROLS ROW (Slider + Reset + Clear) ----------
            controls_row = QHBoxLayout()
            controls_row.setSpacing(10)
            controls_row.setContentsMargins(0, 0, 0, 0)

            # Weight slider
            weight_slider = QSlider(Qt.Horizontal)
            weight_slider.setRange(0, 100)
            weight_slider.setValue(0)
            self.weight_sliders.append(weight_slider)

            slider_container = QHBoxLayout()
            slider_container.setSpacing(5)
            slider_container.addWidget(QLabel("Weight:"))
            slider_container.addWidget(weight_slider)

            controls_row.addLayout(slider_container, 3)

            # Reset and Clear buttons in same row
            reset_btn = QToolButton()
            reset_btn.setText("Reset")
            reset_btn.setObjectName("reset_button")
            self.reset_buttons.append(reset_btn)

            clear_btn = QToolButton()
            clear_btn.setText("Clear Image")
            clear_btn.setObjectName("clear_button")
            self.clear_buttons.append(clear_btn)

            btn_row = QHBoxLayout()
            btn_row.setSpacing(5)
            btn_row.addWidget(reset_btn)
            btn_row.addWidget(clear_btn)

            controls_row.addLayout(btn_row, 1)

            viewport_layout.addLayout(controls_row)

            # ---------- COMPONENT SELECTOR BELOW ----------
            selector_row = QHBoxLayout()
            selector_row.setSpacing(5)

            component_selector = SegmentedControl(["Select Mode"])
            self.component_selectors.append(component_selector)
            selector_row.addWidget(component_selector)

            viewport_layout.addLayout(selector_row)

            # Add viewport to grid
            row = i // 2
            col = i % 2
            self.image_grid.addWidget(viewport_group, row, col)

        # Add grid to main layout
        self.main_layout.addWidget(self.image_grid_widget, 3)

    def setup_control_panel(self):
        # Dedicated right-side control panel
        self.control_panel = QWidget()
        self.control_panel_layout = QVBoxLayout(self.control_panel)
        self.control_panel_layout.setAlignment(Qt.AlignTop)
        self.control_panel.setProperty("class", "control_panel")

        # 1. FT Component Selection (Global Mode Selector)
        ft_group = QGroupBox("FT Component Mode (Global)")
        ft_layout = QVBoxLayout(ft_group)
        self.ft_mode_selector = SegmentedControl(["Magnitude / Phase", "Real / Imaginary"])
        ft_layout.addWidget(self.ft_mode_selector)
        self.control_panel_layout.addWidget(ft_group)

        # 2. Region Selection
        region_group = QGroupBox("Region Selection")
        region_layout = QVBoxLayout(region_group)

        # Segmented control for Inner/Outer/None
        self.region_mode_selector = SegmentedControl(["Inner (Low Freq)", "Outer (High Freq)", "None"])
        region_layout.addWidget(self.region_mode_selector)

        region_layout.addWidget(QLabel("Region Size:"))
        self.region_size_slider = QSlider(Qt.Horizontal)
        self.region_size_slider.setRange(50, 400)  # Min 50, Max 400
        self.region_size_slider.setValue(200)
        region_layout.addWidget(self.region_size_slider)

        self.control_panel_layout.addWidget(region_group)

        # 3. Output Viewports
        output_group = QGroupBox("Mixed Output")
        output_layout = QVBoxLayout(output_group)

        self.output_selector = SegmentedControl(["Output 1", "Output 2"])
        output_layout.addWidget(self.output_selector)

        self.output_image_1 = QLabel("Mixed Image 1")
        self.output_image_2 = QLabel("Mixed Image 2")

        # Set policies to allow images to expand vertically (two rows) and horizontally
        self.output_image_1.setProperty("class", "output_image_label")
        self.output_image_1.setScaledContents(True)
        self.output_image_1.setAlignment(Qt.AlignCenter)
        self.output_image_1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.output_image_1.setMinimumSize(150, 150)

        self.output_image_2.setProperty("class", "output_image_label")
        self.output_image_2.setScaledContents(True)
        self.output_image_2.setAlignment(Qt.AlignCenter)
        self.output_image_2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.output_image_2.setMinimumSize(150, 150)

        # Add images directly to the vertical layout with equal vertical stretch
        output_layout.addWidget(self.output_image_1, 1)
        output_layout.addWidget(self.output_image_2, 1)

        self.control_panel_layout.addWidget(output_group, 1)

        # 4. Status and Control
        self.status_label = QLabel("Ready")
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        self.cancel_button = QPushButton("Save Mixed Output")
        self.control_panel_layout.addWidget(self.cancel_button)

        self.quit_button = QPushButton("Quit Application")
        self.quit_button.setProperty("class", "quit_button")
        self.control_panel_layout.addWidget(self.quit_button)

        self.main_layout.addWidget(self.control_panel, 1)

    def connect_signals(self):
        # Connect to the core logic layer
        for i, label in enumerate(self.input_labels):
            # Set up image loading on double click
            label.mouseDoubleClickEvent = lambda event, idx=i: self.app_logic.load_image(idx)
            # Set up brightness/contrast drag
            label.setMouseTracking(True)
            label.mousePressEvent = lambda event, idx=i: self.app_logic.mouse_press_event(event, idx)
            label.mouseMoveEvent = lambda event, idx=i: self.app_logic.mouse_move_event(event, idx)

            # Reset Button (for B/C)
            self.reset_buttons[i].clicked.connect(lambda checked, idx=i: self.app_logic.reset_brightness_contrast(idx))

            # Connect Clear Button
            self.clear_buttons[i].clicked.connect(lambda checked, idx=i: self.app_logic.clear_image(idx))

            # Weight Slider
            current_slider = self.weight_sliders[i]
            self.weight_sliders[i].sliderReleased.connect(
                (lambda idx_fixed, slider_obj:
                 lambda: self.app_logic.update_weight(slider_obj.value(), idx_fixed)
                 )(i, current_slider)
            )
            # Component Selector (SegmentedControl)
            self.component_selectors[i].selection_changed.connect(self.app_logic.handle_component_selection)

        # Connect new modern components
        self.ft_mode_selector.selection_changed.connect(self.app_logic.handle_ft_mode_change)
        self.region_mode_selector.selection_changed.connect(self.app_logic.handle_region_mode_change)

        # Region Size Slider
        current_slider = self.region_size_slider
        self.region_size_slider.valueChanged.connect(
            (lambda slider_obj:
             lambda: self.app_logic.handle_region_size_change(slider_obj.value())
             )(current_slider)
        )
        self.region_size_slider.sliderReleased.connect(self.app_logic.full_update_cycle)

        self.quit_button.clicked.connect(self.close)

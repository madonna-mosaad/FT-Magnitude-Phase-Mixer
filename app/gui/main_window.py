from PyQt5.QtWidgets import QMainWindow, QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QComboBox, QPushButton, QProgressBar, QGroupBox, \
    QButtonGroup, QToolButton, QSizePolicy  # QSizePolicy imported for layout control
from PyQt5.QtCore import Qt
from app.gui.ui_components import SegmentedControl  # Import the new component


class MainWindow(QMainWindow):
    def __init__(self, app_logic):
        super().__init__()
        self.app_logic = app_logic  # Reference to the logic/core layer
        self.setWindowTitle("FT Image Mixer Pro")
        self.setGeometry(100, 100, 1400, 800)
        self.setMinimumSize(1200, 700)

        # Main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)

        self.setup_main_interface()
        self.setup_control_panel()
        self.connect_signals()

        # Connect QMainWindow's close event to the cleanup logic
        self.closeEvent = self.handle_close_event

    def handle_close_event(self, event):
        """Intercepts the close event to ensure threads are shut down."""
        self.app_logic.cleanup_on_exit()
        event.accept()

    def setup_main_interface(self):
        # 2x2 Grid for Image Viewports
        self.image_grid_widget = QWidget()
        self.image_grid = QGridLayout(self.image_grid_widget)
        self.image_grid.setSpacing(10)

        # Store labels and controls for easy access
        self.input_labels = []
        self.ft_labels = []
        self.weight_sliders = []
        self.component_combos = []
        self.reset_buttons = []
        # NEW: For Brightness/Contrast feedback
        self.adjustment_status_labels = []

        for i in range(4):
            # Viewport Group
            viewport_group = QGroupBox(f"Viewport {i + 1}")
            viewport_layout = QVBoxLayout(viewport_group)

            # Input Image (Original) + FT Component (Interactive) in a horizontal split
            image_h_layout = QHBoxLayout()
            input_label = QLabel("Click to Load Image")
            input_label.setProperty("class", "input_image_label")
            input_label.setScaledContents(True)
            input_label.setAlignment(Qt.AlignCenter)
            # FIX 1: Set a minimum size to prevent the label from collapsing/jumping
            input_label.setMinimumSize(250, 250)
            self.input_labels.append(input_label)

            ft_label = QLabel("FT Component View")
            ft_label.setProperty("class", "ft_component_label")
            ft_label.setScaledContents(True)
            ft_label.setAlignment(Qt.AlignCenter)
            # FIX 1: Set a minimum size (proportional to input)
            ft_label.setMinimumSize(180, 250)
            self.ft_labels.append(ft_label)

            image_h_layout.addWidget(input_label, 3)  # Give input more space
            image_h_layout.addWidget(ft_label, 2)

            # Controls beneath the images
            control_h_layout = QHBoxLayout()

            # B/C Feedback Label
            adj_label = QLabel("B: 0 | C: 1.00")
            # --- THEME CHANGE: Updated color to Teal accent for B/C status label ---
            adj_label.setStyleSheet("font-size: 8pt; color: #00FFFF;")
            self.adjustment_status_labels.append(adj_label)

            weight_slider = QSlider(Qt.Horizontal)
            weight_slider.setRange(0, 100)
            weight_slider.setValue(0)
            self.weight_sliders.append(weight_slider)

            combo = QComboBox()
            combo.setEditable(False)
            # FIX 2: Set the combo box's size policy to fixed horizontally.
            # This prevents it from changing the layout size when its content changes (e.g., toggling FT mode).
            combo.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            self.component_combos.append(combo)

            reset_btn = QToolButton()
            reset_btn.setText("Reset")
            self.reset_buttons.append(reset_btn)

            control_h_layout.addWidget(adj_label)  # New feedback label
            control_h_layout.addWidget(QLabel("Weight:"))
            control_h_layout.addWidget(weight_slider)
            control_h_layout.addWidget(combo)
            control_h_layout.addWidget(reset_btn)

            viewport_layout.addLayout(image_h_layout)
            viewport_layout.addLayout(control_h_layout)

            # Add to the 2x2 grid
            row = i // 2
            col = i % 2
            self.image_grid.addWidget(viewport_group, row, col)

        self.main_layout.addWidget(self.image_grid_widget, 3)  # Give the image grid 3/4 of the space

    def setup_control_panel(self):
        # Dedicated right-side control panel
        self.control_panel = QWidget()
        self.control_panel_layout = QVBoxLayout(self.control_panel)
        self.control_panel_layout.setAlignment(Qt.AlignTop)
        self.control_panel.setProperty("class", "control_panel")

        # 1. FT Component Selection (New Segmented Control)
        ft_group = QGroupBox("FT Component Mode")
        ft_layout = QVBoxLayout(ft_group)
        self.ft_mode_selector = SegmentedControl(["Magnitude / Phase", "Real / Imaginary"])
        ft_layout.addWidget(self.ft_mode_selector)
        self.control_panel_layout.addWidget(ft_group)

        # 2. Region Selection
        region_group = QGroupBox("Region Selection")
        region_layout = QVBoxLayout(region_group)

        # Segmented control for Inner/Outer/None (replacing radio buttons)
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

        self.output_selector = QComboBox()
        self.output_selector.addItems(["Output 1", "Output 2"])
        output_layout.addWidget(self.output_selector)

        # --- FIX: Rework output images for stability and two rows (vertical layout) ---
        self.output_image_1 = QLabel("Mixed Image 1")
        self.output_image_2 = QLabel("Mixed Image 2")

        # Set policies to allow images to expand vertically (two rows) and horizontally
        # Use QSizePolicy.Expanding for both to fill the available space evenly.
        self.output_image_1.setProperty("class", "output_image_label")
        self.output_image_1.setScaledContents(True)
        self.output_image_1.setAlignment(Qt.AlignCenter)
        self.output_image_1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.output_image_1.setMinimumSize(150, 150)  # Stable base size

        self.output_image_2.setProperty("class", "output_image_label")
        self.output_image_2.setScaledContents(True)
        self.output_image_2.setAlignment(Qt.AlignCenter)
        self.output_image_2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.output_image_2.setMinimumSize(150, 150)  # Stable base size

        # Add images directly to the vertical layout with equal vertical stretch
        output_layout.addWidget(self.output_image_1, 1)
        output_layout.addWidget(self.output_image_2, 1)

        # Give the output group a stretch factor of 1 (which now allocates all remaining space)
        self.control_panel_layout.addWidget(output_group, 1)

        # 4. Status and Control (Remove Status Group and place buttons directly)

        # NOTE: Status widgets are created as members, but not added to the layout
        # to free up space while keeping the application logic functional.
        self.status_label = QLabel("Ready")
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        # Place Cancel Button directly in the control panel layout
        self.cancel_button = QPushButton("Cancel Mixing")
        self.control_panel_layout.addWidget(self.cancel_button)

        self.quit_button = QPushButton("Quit Application")
        self.quit_button.setProperty("class", "quit_button")
        self.control_panel_layout.addWidget(self.quit_button)

        self.main_layout.addWidget(self.control_panel, 1)  # Give control panel 1/4 of the space

    def connect_signals(self):
        # Connect to the core logic layer
        for i, label in enumerate(self.input_labels):
            # Set up image loading on double click
            label.mouseDoubleClickEvent = lambda event, idx=i: self.app_logic.load_image(idx)
            # Set up brightness/contrast drag (requires binding to mouse events in main.py)
            label.setMouseTracking(True)
            label.mousePressEvent = lambda event, idx=i: self.app_logic.mouse_press_event(event, idx)
            label.mouseMoveEvent = lambda event, idx=i: self.app_logic.mouse_move_event(event, idx)

            # Reset Button: Use lambda only to capture index, since the clicked signal sends a bool (checked)
            self.reset_buttons[i].clicked.connect(lambda checked, idx=i: self.app_logic.reset_brightness_contrast(idx))

            # FIX for TypeError: sliderReleased emits NO arguments.
            # We capture the index and the slider object, then call slider_obj.value() in the inner lambda.
            current_slider = self.weight_sliders[i]
            self.weight_sliders[i].sliderReleased.connect(
                (lambda idx_fixed, slider_obj:
                 lambda: self.app_logic.update_weight(slider_obj.value(), idx_fixed)
                 )(i, current_slider)
            )
            self.component_combos[i].currentIndexChanged.connect(self.app_logic.handle_component_selection)

        # Connect new modern components
        self.ft_mode_selector.selection_changed.connect(self.app_logic.handle_ft_mode_change)
        self.region_mode_selector.selection_changed.connect(self.app_logic.handle_region_mode_change)

        # Region Size Slider: FIX for TypeError (sliderReleased emits no arguments)
        current_slider = self.region_size_slider
        self.region_size_slider.valueChanged.connect(
            (lambda slider_obj:
             lambda: self.app_logic.handle_region_size_change(slider_obj.value())
             )(current_slider)
        )
        self.region_size_slider.sliderReleased.connect(self.app_logic.full_update_cycle)

        # Connect thread control
        self.cancel_button.clicked.connect(self.app_logic.cancel_mixing)
        self.quit_button.clicked.connect(self.close)

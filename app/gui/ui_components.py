from PyQt5.QtWidgets import QWidget, QHBoxLayout, QToolButton, QSizePolicy
from PyQt5.QtCore import pyqtSignal


class SegmentedControl(QWidget):
    """A modern, segmented control widget to replace radio buttons."""

    # Signal that emits the text of the selected button
    selection_changed = pyqtSignal(str)

    def __init__(self, items, parent=None):
        super().__init__(parent)
        self.items = items
        self.buttons = []
        self.current_selection = None
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(1)  # Gap between buttons

        self.setup_ui()

    def setup_ui(self):
        for i, text in enumerate(self.items):
            btn = QToolButton(self)
            btn.setText(text)
            btn.setCheckable(True)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.setProperty("class", "segmented_control_button")

            # Apply pseudo-classes for styling
            if i == 0:
                btn.setProperty("is_first", True)
            elif i == len(self.items) - 1:
                btn.setProperty("is_last", True)

            btn.clicked.connect(lambda checked, t=text, b=btn: self._on_button_clicked(checked, t, b))
            self.buttons.append(btn)
            self.layout.addWidget(btn)

        # Set the first item as default selected
        if self.buttons:
            self.buttons[0].setChecked(True)
            self.current_selection = self.buttons[0].text()
            # Note: Styling for checked state is handled in dark_theme.qss using the :checked selector.
            # We don't need inline styling here unless absolutely necessary.

    def _on_button_clicked(self, checked, text, clicked_button):
        if not checked:
            # Prevents deselecting the currently selected button
            clicked_button.setChecked(True)
            return

        # Deselect all other buttons and update styling
        for btn in self.buttons:
            if btn is not clicked_button:
                btn.setChecked(False)

        self.current_selection = text
        self.selection_changed.emit(text)

    def get_selection(self):
        return self.current_selection

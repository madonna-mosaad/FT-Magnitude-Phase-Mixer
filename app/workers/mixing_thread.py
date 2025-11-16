import threading
import time
import logging
from PyQt5.QtCore import QObject, pyqtSignal

# Configure logging for the worker
logging.basicConfig(filemode="a", filename="mixer_log.log",
                    format="(%(asctime)s) | %(name)s| %(levelname)s | => %(message)s", level=logging.INFO)


# A QObject to safely emit signals from the worker thread back to the main thread
class MixingThreadSignals(QObject):
    """Signals available from the worker thread to the main thread."""
    finished = pyqtSignal(object)  # Emits the resulting image (np.ndarray)
    progress = pyqtSignal(int)
    error = pyqtSignal(str)
    canceled = pyqtSignal()


class MixingThread(threading.Thread):
    def __init__(self, main_logic, signals: MixingThreadSignals):
        super().__init__()
        self.main_logic = main_logic  # Reference to the ApplicationLogic object
        self.signals = signals
        self._is_canceled = False  # Use a simple flag for cancellation
        self.steps = 5  # Number of progress steps for simulation

    def run(self):
        try:
            self.signals.progress.emit(0)

            # Simulate work time and report progress
            for i in range(self.steps):
                if self._is_canceled:
                    self.signals.canceled.emit()
                    logging.info('Mixing thread canceled.')
                    return

                time.sleep(0.1)  # Simulate work time for one step

                # Update progress bar
                progress_value = int((i + 1) / self.steps * 100)
                self.signals.progress.emit(progress_value)

            # --- Actual Mixing Logic Execution ---
            if not self._is_canceled:
                result_image = self.main_logic.execute_mixing_core()

                # Reset progress to 100%
                self.signals.progress.emit(100)

                self.signals.finished.emit(result_image)
                logging.info('Mixing thread completed successfully.')

        except Exception as e:
            self.signals.error.emit(f"Error in mixing thread: {e}")
            logging.error(f'Error in mixing thread: {e}')
            self.signals.progress.emit(0)  # Reset progress on error

        # Ensure the thread's run method finishes

    def cancel(self):
        """Sets the flag to cancel the thread gracefully."""
        self._is_canceled = True
        # IMPORTANT: Do NOT call self.join() here, as it can cause deadlocks if called from the main thread.

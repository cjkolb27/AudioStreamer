import sys
from PyQt5 import QtWidgets, QtCore
from pathlib import Path

# Dummy backend – replace with real logic
class AudioStreamer(QtCore.QObject):
    status_changed = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.running = False

    def start(self, hostname, port):
        print(f"Starting stream to {hostname}:{port}")
        self.running = True
        self.status_changed.emit(f"Running → {hostname}:{port}")
        with open((Path(__file__).parent / "Data" / "info.txt"), "w", newline='') as info:
            info.write(f"{hostname}\r\n{port}\r\n")

    def stop(self):
        print("Stopping stream")
        self.running = False
        self.status_changed.emit("Stopped")

# ------------------------------------------------------------------
class MainWindow(QtWidgets.QWidget):
    def __init__(self, streamer: AudioStreamer):
        super().__init__()
        self.streamer = streamer

        # UI elements
        ip_label   = QtWidgets.QLabel("Hostname:")
        self.ip_edit  = QtWidgets.QLineEdit("")

        port_label = QtWidgets.QLabel("Port:")
        self.port_spin = QtWidgets.QSpinBox()
        self.port_spin.setRange(1, 65535)
        self.port_spin.setValue(1)
        with open((Path(__file__).parent / "Data" / "info.txt"), "r", newline='') as info:
            self.ip_edit  = QtWidgets.QLineEdit(info.readline().replace("\r\n", ""))
            self.port_spin.setValue(int(info.readline()))

        self.status_lbl = QtWidgets.QLabel("Stopped")

        start_btn = QtWidgets.QPushButton("Start")
        stop_btn  = QtWidgets.QPushButton("Stop")

        # Layout
        form_layout = QtWidgets.QFormLayout()
        form_layout.addRow(ip_label, self.ip_edit)
        form_layout.addRow(port_label, self.port_spin)

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addWidget(start_btn)
        btn_layout.addWidget(stop_btn)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.status_lbl)
        main_layout.addLayout(btn_layout)

        # Connections
        start_btn.clicked.connect(self.on_start)
        stop_btn.clicked.connect(self.streamer.stop)
        self.streamer.status_changed.connect(self.status_lbl.setText)

    def on_start(self):
        if self.streamer.running:
            QtWidgets.QMessageBox.information(self, "Info", "Already running")
            return
        dest_ip = self.ip_edit.text()
        dest_port = self.port_spin.value()
        self.streamer.start(dest_ip, dest_port)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    streamer = AudioStreamer()
    win = MainWindow(streamer)
    win.setWindowTitle("Python Audio Streamer")
    win.resize(300, 150)
    win.show()
    sys.exit(app.exec_())

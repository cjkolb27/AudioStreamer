import sys
import socket
import threading
import os
from PyQt5 import QtWidgets, QtCore
from pathlib import Path
import numpy
import struct
import pyaudio

# Dummy backend – replace with real logic
class AudioStreamer(QtCore.QObject):
    status_changed = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.running = False
    
    def writeSettings(self, hostname, port, sc):
        with open((Path(__file__).parent / "Data" / "info.txt"), "w", newline='') as info:
            info.write(f"{hostname}\r\n{port}\r\n{sc}\r\n")

    def start(self, hostname, port, sc):
        print(f"Starting stream to {hostname}:{port}")
        self.running = True
        self.status_changed.emit(f"Running → {hostname}:{port}")
        with open((Path(__file__).parent / "Data" / "info.txt"), "w", newline='') as info:
            info.write(f"{hostname}\r\n{port}\r\n{sc}\r\n")

    def stop(self):
        print("Stopping stream")
        self.running = False
        self.status_changed.emit("Stopped")
        End[0] = True

    def flipflop(self, server):
        print(f"{server} Flipped")


class MainWindow(QtWidgets.QWidget):
    def __init__(self, streamer: AudioStreamer):
        super().__init__()
        self.streamer = streamer

        self.thread = None

        # UI elements
        self.hostname_label   = QtWidgets.QLabel("Hostname:")
        self.hostname_edit  = QtWidgets.QLineEdit("")

        self.port_label = QtWidgets.QLabel("Server Port:")
        self.port_spin = QtWidgets.QSpinBox()
        self.port_spin.setRange(1, 65535)
        self.port_spin.setValue(1)
        self.serverclient = "True"
        with open((Path(__file__).parent / "Data" / "info.txt"), "r", newline='') as info:
            self.hostname_edit = QtWidgets.QLineEdit(info.readline().replace("\r\n", ""))
            self.port_spin.setValue(int(info.readline()))
            self.serverclient = info.readline().replace("\r\n", "")

        self.status_lbl = QtWidgets.QLabel("Stopped")

        p = pyaudio.PyAudio()
        for i in range(p.get_device_count()):
            dev = p.get_device_info_by_index(i)
            print(f"Index: {i}, Name: {dev['name']}, Host API: {dev['hostApi']}")

        p.terminate()

        pa = pyaudio.PyAudio()
        print(pa.get_device_info_by_index(input))
        pa.terminate()

        self.server_btn = QtWidgets.QPushButton("Server")
        self.server_btn.setCheckable(True)
        self.server_btn.setFixedSize(130, 40)
        self.client_btn = QtWidgets.QPushButton("Client")
        self.client_btn.setCheckable(True)
        self.client_btn.setFixedSize(130, 40)
        self.start_btn = QtWidgets.QPushButton("Start")
        self.stop_btn  = QtWidgets.QPushButton("Stop")

        group = QtWidgets.QButtonGroup(self)
        group.setExclusive(True)
        group.addButton(self.server_btn, 1)
        group.addButton(self.client_btn, 2)

        # Layout
        form_layout = QtWidgets.QFormLayout()
        form_layout.addRow(self.server_btn, self.client_btn)
        form_layout.addRow(self.hostname_label, self.hostname_edit)
        form_layout.addRow(self.port_label, self.port_spin)

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.status_lbl)
        main_layout.addLayout(btn_layout)

        # Connections
        self.server_btn.toggled.connect(self.on_flipflop)
        self.start_btn.clicked.connect(self.on_start)
        self.stop_btn.clicked.connect(self.on_stop)
        self.streamer.status_changed.connect(self.status_lbl.setText)
        if self.serverclient == "True":
            self.server_btn.setChecked(True)
        else:
            self.client_btn.setChecked(True)
        self.stop_btn.setEnabled(False)
    
    def on_flipflop(self, checked: bool):
        self.streamer.flipflop(checked)
        dest_ip = self.hostname_edit.text()
        dest_port = self.port_spin.value()
        if checked:
            self.serverclient = "True"
            self.hostname_edit.setEnabled(False)
        else:
            self.serverclient = "False"
            self.hostname_edit.setEnabled(True)
        self.streamer.writeSettings(dest_ip, dest_port, self.serverclient)
    
    def on_stop(self):
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.client_btn.setEnabled(True)
        self.server_btn.setEnabled(True)
        self.streamer.stop()
        self.thread.join()
        self.thread = None

    def on_start(self):
        if self.streamer.running:
            QtWidgets.QMessageBox.information(self, "Info", "Already running")
            return
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        dest_hostname = self.hostname_edit.text()
        dest_port = self.port_spin.value()
        sc = self.serverclient
        self.streamer.start(dest_hostname, dest_port, sc)
        if self.serverclient == "True":
            self.client_btn.setEnabled(False)
            self.thread = threading.Thread(target=tryConnect, args=(True, socket.gethostname(), int(dest_port)))
        else:
            self.server_btn.setEnabled(False)
            self.thread = threading.Thread(target=tryConnect, args=(False, dest_hostname, int(dest_port)))
        self.thread.start()

def tryConnect(server, host, port):
    print("Thread Started")
    if server:
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f"{host} {port}")
        serverSocket.bind((host, port))
        serverSocket.listen(1)
        print("Listening for client")
        connId, addr = serverSocket.accept()
        print("Found client")
        
        pa = pyaudio.PyAudio()
        stream = pa.open(format=pyaudio.paInt16, channels=channels, rate=rate, input=True, input_device_index=input, frames_per_buffer=1024)
        print("Created stream")

        try:
            while not End[0]:
                data = stream.read(1024, exception_on_overflow=False)
                connId.sendall(struct.pack('>I', len(data)) + data)
        except Exception as e:
            print(e)
            pass
        
        stream.stop_stream()
        stream.close()
        pa.terminate()
        connId.close()
        serverSocket.close()
        print("Server closed connections")
    else:
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Looking for server")
        try:
            clientSocket.connect((host, port))
        except OSError:
            return
        print("Server found")

        pa = pyaudio.PyAudio()
        stream = pa.open(format=pyaudio.paInt16, channels=channels, rate=rate, output=True, output_device_index=input, frames_per_buffer=1024)

        try:
            while not End[0]:

                read = clientSocket.recv(4)
                if not read:
                    break
                msglen = struct.unpack('>I', read)[0]
                data = b''
                while len(data) < msglen:
                    packet = clientSocket.recv(msglen - len(data))
                    if not packet:
                        raise RuntimeError("Socket closed prematurely")
                    data += packet

                stream.write(data)
        except Exception:
            pass
        stream.stop_stream()
        stream.close()
        pa.terminate()
        clientSocket.close()
        print("Client closed connections")
    return

if __name__ == "__main__":
    End = [True]
    End[0] = False
    rate = 44100
    channels = 2
    blocksize = 1024
    input = 14
    app = QtWidgets.QApplication(sys.argv)
    streamer = AudioStreamer()
    win = MainWindow(streamer)
    win.setWindowTitle("Python Audio Streamer")
    win.resize(300, 150)
    win.show()
    sys.exit(app.exec_())

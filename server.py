import socket
import numpy as np
import sounddevice as sd

device_name = "CABLE Output (VB-Audio Virtual Cable), Windows WASAPI"
TARGET_IP   = socket.gethostbyname("Beefy-PC")   # <-- change to receiver's IP
TARGET_PORT = 2828            # must match the receiver
CHUNK_SIZE  = 1024             # frames per block (≈ 23 ms @ 44.1 kHz)
FORMAT      = np.int16

# ------------------------------------------------------------------
# 1️⃣  Create a UDP socket once – no connect() needed
# ------------------------------------------------------------------
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# ------------------------------------------------------------------
# 2️⃣  Audio callback: send each block immediately
# ------------------------------------------------------------------
def audio_callback(indata, frames, time, status):
    if status:
        print("Audio error:", status)
    # Convert to raw bytes (little‑endian int16) and send
    sock.sendto(indata.tobytes(), (TARGET_IP, TARGET_PORT))

# ------------------------------------------------------------------
# 3️⃣  Open the microphone stream
# ------------------------------------------------------------------
with sd.InputStream(samplerate=48000,
                    blocksize=CHUNK_SIZE,
                    dtype="int16",
                    channels=1,
                    device=device_name,
                    callback=audio_callback):
    print(f"Streaming to {TARGET_IP}:{TARGET_PORT} …")
    try:
        while True:                # keep the main thread alive
            sd.sleep(1000)
    except KeyboardInterrupt:
        pass

print("\nSender stopped.")
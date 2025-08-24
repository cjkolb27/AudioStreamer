import socket
import numpy as np
import sounddevice as sd

LISTEN_IP   = socket.gethostbyname("Beefy-PC")     # listen on all interfaces (or specific IP)
LISTEN_PORT = 2828         # must match the sender's port
CHUNK_SIZE  = 1024          # frames per block – same as sender
FORMAT      = np.int16

# ------------------------------------------------------------------
# 1️⃣  Create a UDP socket and bind to our listening address
# ------------------------------------------------------------------
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((LISTEN_IP, LISTEN_PORT))
print(f"Listening on {LISTEN_IP}:{LISTEN_PORT}")

# ------------------------------------------------------------------
# 2️⃣  Prepare the output stream (no callback needed – we’ll write manually)
# ------------------------------------------------------------------
stream = sd.OutputStream(samplerate=44100,
                         blocksize=CHUNK_SIZE,
                         dtype="int16",
                         channels=1)

stream.start()

try:
    # ------------------------------------------------------------------
    # 3️⃣  Main loop – receive UDP packets and play
    # ------------------------------------------------------------------
    while True:
        data, _addr = sock.recvfrom(CHUNK_SIZE * FORMAT().nbytes)
        if not data:           # should never happen with UDP, but guard anyway
            continue

        # Convert raw bytes back into a NumPy array
        samples = np.frombuffer(data, dtype=FORMAT)

        print(samples)

        # If we get a truncated packet (rare), pad it:
        if len(samples) < CHUNK_SIZE:
            samples = np.pad(samples, (0, CHUNK_SIZE - len(samples)), 'constant')

        stream.write(samples)
except KeyboardInterrupt:
    pass

# ------------------------------------------------------------------
# 4️⃣  Clean up
# ------------------------------------------------------------------
stream.stop()
stream.close()
sock.close()
print("\nReceiver stopped.")
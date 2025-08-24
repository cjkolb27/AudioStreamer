import sounddevice as sd
import soundfile as sf

# Pick the device index or name you saw earlier
device_name = "CABLE Output (VB-Audio Virtual Cable), Windows WASAPI"
samplerate = 48000
channels = 2
duration = 5  # seconds

print("Recording...")
recording = sd.rec(
    int(duration * samplerate),
    samplerate=samplerate,
    channels=channels,
    device=device_name
)
sd.wait()
print("Done.")

# Save to WAV
sf.write("Data/recording.wav", recording, samplerate)
print("Saved to desktop_audio.wav")

import numpy as np
import sounddevice as sd

sample_rate = 48000  # Samples per second
chunk_size = 512    # Number of samples per chunk

def list_devices():
    print("Available audio devices:")
    devices = sd.query_devices()
    for i, dev in enumerate(devices):
        print(f"{i}: {dev['name']}")

def process_chunk(data):
    # Apply a windowing function (Hanning in this case)
    windowed_data = data * np.hanning(len(data))

    # Zero padding
    padded_data = np.zeros(sample_rate)
    padded_data[:len(windowed_data)] = windowed_data

    # Perform FFT
    fft_result = np.fft.fft(padded_data)
    freqs = np.fft.fftfreq(len(padded_data)) * sample_rate

    # Find the dominant frequency using the magnitude spectrum
    magnitude = np.abs(fft_result)
    peak_freq = freqs[np.argmax(magnitude)]

    return abs(peak_freq)

def callback(indata, frames, time, status):
    if status:
        print(status)
    if any(indata):
        dominant_freq = process_chunk(indata[:, 0])
        print(f"Dominant Frequency: {dominant_freq:.2f} Hz")

list_devices()
device_index = int(input("Enter the index of your Scarlett 2i2: "))

# Open a stream
with sd.InputStream(callback=callback, channels=1, samplerate=sample_rate, blocksize=chunk_size, device= device_index):
    print("Streaming started, play your guitar...")
    input("Press Enter to stop...")
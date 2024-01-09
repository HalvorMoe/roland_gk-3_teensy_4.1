import numpy as np
import scipy.fftpack
import sounddevice as sd
import time

# General settings that can be changed by the user
SAMPLE_FREQ = 48000 # sample frequency in Hz
WINDOW_SIZE = 48000 # window size of the DFT in samples
WINDOW_STEP = 12000 # step size of window
NUM_HPS = 5 # max number of harmonic product spectrums
POWER_THRESH = 1e-6 # tuning is activated if the signal power exceeds this threshold
HANN_WINDOW = np.hanning(WINDOW_SIZE)

E_string_frequencies = {
    82.41: 0, 87.31: 1, 92.50: 2, 98.00: 3, 103.83: 4, 
    110.00: 5, 116.54: 6, 123.47: 7, 130.81: 8, 138.59: 9, 
    146.83: 10, 155.56: 11, 164.81: 12, 174.61: 13, 185.00: 14, 
    196.00: 15, 207.65: 16, 220.00: 17, 233.08: 18, 246.94: 19, 
    329.63: 20
}

def find_closest_fret(frequency, frequency_mapping):
    """
    This function finds the closest fret for a given frequency on the E string.
    Parameters:
        frequency (float): The detected frequency.
        frequency_mapping (dict): Mapping of frequencies to fret numbers.
    Returns:
        closest_fret (int): The fret number that is closest to the detected frequency.
    """
    closest_frequency = min(frequency_mapping.keys(), key=lambda x:abs(x-frequency))
    return frequency_mapping[closest_frequency]

def callback(indata, frames, time, status):
  if not hasattr(callback, "window_samples"):
    callback.window_samples = [0 for _ in range(WINDOW_SIZE)]

  if status:
    print(status)
    return
  if any(indata):
    callback.window_samples = np.concatenate((callback.window_samples, indata[:, 0])) # append new samples
    callback.window_samples = callback.window_samples[len(indata[:, 0]):] # remove old samples



    hann_samples = callback.window_samples * HANN_WINDOW
    magnitude_spec = abs(scipy.fftpack.fft(hann_samples)[:len(hann_samples)//2])

    # interpolate spectrum
    mag_spec_ipol = np.interp(np.arange(0, len(magnitude_spec), 1/NUM_HPS), np.arange(0, len(magnitude_spec)), magnitude_spec)
    mag_spec_ipol = mag_spec_ipol / np.linalg.norm(mag_spec_ipol, ord=2) # normalize it

    hps_spec = mag_spec_ipol
    # calculate the HPS
    for i in range(1, NUM_HPS):
      hps_spec = np.multiply(hps_spec[:int(np.ceil(len(mag_spec_ipol)/(i+1)))], mag_spec_ipol[::(i+1)])

    max_ind = np.argmax(hps_spec)
    max_freq = max_ind * (SAMPLE_FREQ/WINDOW_SIZE) / NUM_HPS
    max_freq = round(max_freq, 1)

    closest_fret = find_closest_fret(max_freq, E_string_frequencies)
    print(closest_fret)

try:
  print("Starting HPS guitar tuner...")
  with sd.InputStream(channels=1, callback=callback, blocksize=WINDOW_STEP, samplerate=SAMPLE_FREQ, device=18):
    while True:
      time.sleep(0) # reduced sleep time to update frequency faster
except Exception as exc:
  print(str(exc))

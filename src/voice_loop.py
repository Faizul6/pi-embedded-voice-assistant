import json
import datetime
import os
import subprocess
import sys
import numpy as np
import pyaudio
from vosk import KaldiRecognizer, Model

try:
    import oled_display
except ImportError:
    oled_display = None

DEVICE_INDEX = 0
NATIVE_RATE = 48000
TARGET_RATE = 16000


def downsample(data_bytes, native_rate=NATIVE_RATE, target_rate=TARGET_RATE):
    audio = np.frombuffer(data_bytes, dtype=np.int16)
    factor = native_rate // target_rate
    downsampled = audio[::factor]
    return downsampled.tobytes()


def read_kernel_rtc_time():
    try:
        with open("/sys/class/rtc/rtc0/time", "r") as f:
            return f.read().strip()
        with open("/sys/class/rtc/rtc0/date", "r") as f:
            date_str = f.read().strip()
        utc_dt = datetime.striptime(f"{date-str} {utc_str}" , "%Y-%m-%d %H:%M:%S")
        utc_dt = utc_dt.replace (tzinfo = timezone.utc)
        return local_dt.strftime("%H:%M:%S") 
    except Exception as e:
        return f"RTC Error: {e}"


def read_kernel_rtc_date():
    try:
        with open("/sys/class/rtc/rtc0/date", "r") as f:
            return f.read().strip()
    except Exception as e:
        return f"RTC Error: {e}"


def update_display(line1, line2=""):
    print(f"[OLED] {line1} | {line2}")
    if oled_display and hasattr(oled_display, "show_text"):
        oled_display.show_text(line1, line2)


def speak(text, active_stream, audio_interface):
    """Destroy PyAudio bindings, play WAV directly via ALSA, and rebuild."""
    # 1. Completely destroy the C-level ALSA lock
    active_stream.stop_stream()
    active_stream.close()
    audio_interface.terminate()

    # 2. Route espeak to a WAV file, then use aplay to explicitly use our ALSA plug
    subprocess.run(["espeak-ng", "-s", "150", "-w", "resp.wav", text])
    subprocess.run(["aplay", "-D", "plughw:0,0", "resp.wav"])

    # 3. Rebuild PyAudio from scratch
    new_pa = pyaudio.PyAudio()
    new_stream = new_pa.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=NATIVE_RATE,
        input=True,
        input_device_index=DEVICE_INDEX,
        frames_per_buffer=6000,
    )
    new_stream.start_stream()
    return new_stream, new_pa


if not os.path.exists("model"):
    print("Error: 'model' directory not found.")
    sys.exit(1)

print("Loading Vosk model...")
model = Model("model")
recognizer = KaldiRecognizer(model, TARGET_RATE)

pa = pyaudio.PyAudio()
stream = pa.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=NATIVE_RATE,
    input=True,
    input_device_index=DEVICE_INDEX,
    frames_per_buffer=6000,
)
stream.start_stream()

print("\n--- System Online. Listening for commands... ---")
update_display("System Ready", "Listening...")

try:
    while True:
        data = stream.read(6000, exception_on_overflow=False)
        data_16k = downsample(data)
        if recognizer.AcceptWaveform(data_16k):
            res = json.loads(recognizer.Result())
            command = res.get("text", "").lower()

            if not command:
                continue

            print(f"\n[Heard]: {command}")

            if "time" in command:
                cur_time = read_kernel_rtc_time()
                update_display("Time (DS3231):", cur_time)
                stream, pa = speak(f"The time is {cur_time}", stream, pa)

            elif "date" in command:
                cur_date = read_kernel_rtc_date()
                update_display("Date (DS3231):", cur_date)
                stream, pa = speak(f"Today is {cur_date}", stream, pa)

            elif "shutdown" in command or "exit" in command:
                update_display("Exiting...", "Goodbye")
                speak("Shutting down voice demonstrator", stream, pa)
                break

            else:
                update_display("Query:", command[:16])

except KeyboardInterrupt:
    print("\nTerminated by user.")
finally:
    try:
        stream.stop_stream()
        stream.close()
        pa.terminate()
    except:
        pass

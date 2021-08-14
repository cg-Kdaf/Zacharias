#!/usr/bin/env python3
import os
import queue
import sounddevice as sd
import vosk
import sys
import json
import fastpunct

q = queue.Queue()

speech_to_text_model = "english_us_small"


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))


try:
    if os.path.exists(os.path.join("models/vosk", speech_to_text_model)):
        print(f"Vosk Speech To Text found with model : '{speech_to_text_model}'.")
    else:
        print("Please download a model for your language from https://alphacephei.com/vosk/models")
        print(f"and unpack as '{speech_to_text_model}' in the Zacharias/models/vosk/ folder.")
        exit(0)

    vosk.SetLogLevel(-1)
    model = vosk.Model(os.path.join("models/vosk", speech_to_text_model))
    device_info = sd.query_devices(None, 'input')
    samplerate = int(device_info['default_samplerate'])

    punct = None
    if os.path.exists("models/fastpunct/english"):
        punct = fastpunct.FastPunct(checkpoint_local_path="models/fastpunct/english")
        print("Punctuation restoration 'fastpunct' library found.")
    else:
        print("Please download a model")
        print("and unpack it in the Zacharias/models/fastpunct/english folder.")

    with sd.RawInputStream(samplerate=samplerate,
                           blocksize=8000,
                           device=None,
                           dtype='int16',
                           channels=1,
                           callback=callback):
        rec = vosk.KaldiRecognizer(model, samplerate)
        rec.SetWords(True)
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                res = json.loads(rec.FinalResult())
                if res['text']:
                    sentence = res['text']
                    sentence = punct.punct(sentence)
                    print("\r\033[K" + sentence)
            else:
                res = json.loads(rec.PartialResult())
                if res['partial']:
                    sentence = res['partial']
                    sentence = punct.punct(sentence)
                    print("\r\033[K" + bcolors.OKGREEN + sentence + bcolors.ENDC, end="")

except KeyboardInterrupt:
    exit(0)
except Exception as e:
    print(type(e).__name__ + ': ' + str(e))

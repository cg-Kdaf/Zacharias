#!/usr/bin/env python3
import queue
import sounddevice as sd
import vosk
import sys
import json
import fastpunct
from private_data import Settings, dl_model_path

q = queue.Queue()
settings = Settings()

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
    vosk.SetLogLevel(-1)
    device_info = sd.query_devices(None, 'input')
    samplerate = int(device_info['default_samplerate'])

    model_path = dl_model_path(settings["vosk"])
    if model_path:
        vosk_model = vosk.Model(model_path)
    else:
        print("Model missing, could not start")
        exit(0)

    model_path = dl_model_path(settings["fastpunct"])
    punct = None
    if model_path:
        punct = fastpunct.FastPunct(checkpoint_local_path=model_path)

    print("Listening")
    with sd.RawInputStream(samplerate=samplerate,
                           blocksize=8000,
                           device=None,
                           dtype='int16',
                           channels=1,
                           callback=callback):
        rec = vosk.KaldiRecognizer(vosk_model, samplerate)
        rec.SetWords(True)
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                res = json.loads(rec.FinalResult())
                if res['text']:
                    sentence = res['text']
                    if punct:
                        sentence = punct.punct(sentence)
                    print("\r\033[K" + sentence)
            else:
                res = json.loads(rec.PartialResult())
                if res['partial']:
                    sentence = res['partial']
                    if punct:
                        sentence = punct.punct(sentence)
                    print("\r\033[K" + bcolors.OKGREEN + sentence + bcolors.ENDC, end="")

except KeyboardInterrupt:
    exit(0)

except Exception as e:
    print(type(e).__name__ + ': ' + str(e))

#!/usr/bin/env python3

import asyncio
import io
import wave
import logging

import pandas as pd
from pathlib import Path

from wyoming.audio import AudioChunk, AudioStop
from wyoming.client import AsyncTcpClient
from wyoming.tts import Synthesize, SynthesizeVoice

_LOGGER = logging.getLogger(__name__)

WYOMONG_PIPER_SERVER=("192.168.0.4", "10200")       # Set this address to your wyoming-piper backend
VOICE="de_DE-glados-high"                           # Select the model, you want to use (here: https://huggingface.co/systemofapwne/piper-de-glados)
INFILE="sound_list_de.csv"                          # Association of voice lines to file names

async def tts(file, sentence):
    async with AsyncTcpClient(*WYOMONG_PIPER_SERVER) as client:

        voice = SynthesizeVoice(name=VOICE)
        synthesize = Synthesize(text=sentence, voice=voice)
        await client.write_event(synthesize.event())

        with io.BytesIO() as wav_io:
            wav_writer: wave.Wave_write | None = None
            while True:
                event = await client.read_event()
                if event is None:
                    _LOGGER.debug("Connection lost")
                    return (None, None)

                if AudioStop.is_type(event.type):
                    break

                if AudioChunk.is_type(event.type):
                    chunk = AudioChunk.from_event(event)
                    if wav_writer is None:
                        wav_writer = wave.open(wav_io, "wb")
                        wav_writer.setframerate(chunk.rate)
                        wav_writer.setsampwidth(chunk.width)
                        wav_writer.setnchannels(chunk.channels)

                    wav_writer.writeframes(chunk.audio)

            if wav_writer is not None:
                wav_writer.close()

            data = wav_io.getvalue()
        
    with open(file, "wb") as f:
        f.write(data)

async def gen_wav_from_csv(file, outdir):
    data = pd.read_csv(file, header = None)
    wav_files = data[0]
    sentences = data[1]
    for i in range(len(wav_files)):
        wav = wav_files[i][:-4] + ".wav"
        sentence = sentences[i].replace(".", ",") # This reduces the pause between sentences significantly
        await tts(file = Path(outdir) / wav, sentence=sentence)


def main():
    loop = asyncio.get_event_loop()
    coroutine = gen_wav_from_csv(file=INFILE, outdir="./output_wav")
    loop.run_until_complete(coroutine)

if __name__ == "__main__":
    main()
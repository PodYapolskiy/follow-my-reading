from pydub import AudioSegment, silence
from os import path, mkdir
from math import log10 as lg


def dbfs_to_percents(dbfs):
    return 10 ** (dbfs / 20)


def percents_to_dbfs(percents):
    return 20 * lg(percents)


def split_audio(file: str | AudioSegment, intervals):
    # file is the path to the file to be split or an object
    # intervals is the set of intervals to be returned in format of [(begin(seconds), end(seconds)),]
    # returns the absolute path to where the split segments were stored

    store_path = "out"

    if not path.exists(store_path):
        mkdir(store_path)

    if type(file) == str:
        audio = AudioSegment.from_file(file, file[file.rfind(".") + 1:])
    elif type(file) == AudioSegment:
        audio = file
    else:
        raise TypeError("Invalid argument")
    for i in range(len(intervals)):
        audio[int(intervals[i][0]*1000):
              int(intervals[i][1]*1000)].export(f"{store_path}/{i}.mp3", format="mp3")

    return path.abspath(store_path)


def split_silence(file, max_interval=30, cutoff_ratio=0.05):
    # file is the file to be split
    # max_interval is the maximum length of the split audio
    # cutoff ratio is the noise level that is accepted for silence as a ratio of the max noise level

    audio = AudioSegment.from_file(file, file[file.rfind(".") + 1:])
    max_dbfs = audio.max_dBFS
    noise_level = percents_to_dbfs(cutoff_ratio * dbfs_to_percents(max_dbfs))

    silence_chunks = silence.detect_silence(audio, min_silence_len=100, silence_thresh=noise_level)
    audio_intervals = []

    max_interval *= 1000
    if silence_chunks[0][0] != 0:
        audio = AudioSegment.silent(100) + audio
        for i in range(len(silence_chunks)):
            silence_chunks[i] = (silence_chunks[i][0] + 100, silence_chunks[i][1] + 100)
        silence_chunks.insert((0, 100), 0)
    if silence_chunks[-1][1] != len(audio):
        silence_chunks.append((len(audio), len(audio) + 100))
        audio = audio + AudioSegment.silent(100)
    new_beg = silence_chunks[0][1] - 50

    for i in range(1, len(silence_chunks)):
        if 50 + silence_chunks[i][0] - new_beg > max_interval:
            audio_intervals.append((new_beg, silence_chunks[i-1][0] + 50))
            new_beg = silence_chunks[i-1][1] - 50

    audio_intervals.append((new_beg, silence_chunks[-1][0]+50))

    return split_audio(audio, [(i[0] / 1000, i[1] / 1000) for i in audio_intervals]), len(audio_intervals)


# split_silence("D:\\Downloads\\TextTo.mp3")


from math import log10 as lg
from os import mkdir, path

from librosa import get_duration
from uuid import uuid4, UUID
from pydub import AudioSegment, silence
from typing import List, Tuple


def duration(audio: str) -> float:
    filepath = "./temp_data/audio/" + audio
    return get_duration(path=filepath)


def dbfs_to_percents(dbfs: float) -> float:
    return 10 ** (dbfs / 20)


def percents_to_dbfs(percents: float) -> float:
    return 20 * lg(percents)


def split_audio(  # type: ignore
    file: str | AudioSegment, intervals: List[Tuple[float, float]]
) -> List[UUID]:
    # file is the path to the file to be split or an object
    # intervals is the set of intervals to be returned in format of [(begin(seconds), end(seconds)),]
    # returns the absolute path to where the split segments were stored

    store_path = "./temp_data/audio"

    if not path.exists(store_path):
        mkdir(store_path)

    if isinstance(file, str):
        audio: AudioSegment = AudioSegment.from_file(file)  # type: ignore
    elif isinstance(file, AudioSegment):
        audio = file
    else:
        raise TypeError("Invalid argument")

    files: List[UUID] = []
    for i in range(len(intervals)):
        file_id = uuid4()
        audio[int(intervals[i][0] * 1000) : int(intervals[i][1] * 1000)].export(
            f"{store_path}/{file_id}", format="mp3"
        )
        files.append(file_id)

    return files


def split_silence(
    file: str, max_interval: float = 30, cutoff_ratio: float = 0.05
) -> Tuple[List[UUID], List[Tuple[int, int]]]:
    # file is the file to be split
    # max_interval is the maximum length of the split audio
    # cutoff ratio is the noise level that is accepted for silence as a ratio of the max noise level

    audio: AudioSegment = AudioSegment.from_file(file, file[file.rfind(".") + 1 :])  # type: ignore
    max_dbfs = audio.max_dBFS
    noise_level = percents_to_dbfs(cutoff_ratio * dbfs_to_percents(max_dbfs))

    silence_chunks = silence.detect_silence(
        audio, min_silence_len=100, silence_thresh=noise_level
    )
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
            audio_intervals.append((new_beg, silence_chunks[i - 1][0] + 50))
            new_beg = silence_chunks[i - 1][1] - 50

    audio_intervals.append((new_beg, silence_chunks[-1][0] + 50))

    return (
        split_audio(audio, [(i[0] / 1000, i[1] / 1000) for i in audio_intervals]),
        audio_intervals,
    )

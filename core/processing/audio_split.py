from math import log10 as lg
from typing import List, Tuple
from uuid import UUID, uuid4

from librosa import get_duration
from pydub import AudioSegment, silence

from config import get_config

config = get_config()


def duration(audio: str) -> float:
    filepath = config.storage.audio_dir / audio
    return get_duration(path=filepath)


def dbfs_to_fraction(dbfs: float) -> float:
    """
    Converts dbfs to fraction of max volume
    :param dbfs: dbfs to be converted
    :return: the fraction (float)
    """
    return 10 ** (dbfs / 20)


def fraction_to_dbfs(fraction: float) -> float:
    """
    Converts percents of max volume into dbfs
    :param fraction: the fraction of max volume
    :return: the dbfs (float)
    """
    return 20 * lg(fraction)


def split_audio(  # type: ignore
    file: str | AudioSegment, intervals: List[Tuple[float, float]]
) -> List[UUID]:
    """
    Splits the audio using timestamps for beginning and end
    Supports mul
    :param file: path to the audio file or pydub.AudioSegment
    :param intervals: a list of segments, given by the timestamps to the beginning and end (in seconds)
    :return: the uuids of the cut-up files (in order of appearance in intervals)
    """

    # Creating the pydub.AudioSegment if it is not already created
    if isinstance(file, str):
        audio: AudioSegment = AudioSegment.from_file(file)  # type: ignore
    elif isinstance(file, AudioSegment):
        audio = file
    else:
        raise TypeError("Invalid argument")

    # Cutting up the file and storing it
    files: List[UUID] = []
    for i in range(len(intervals)):
        file_id = uuid4()
        audio[int(intervals[i][0] * 1000) : int(intervals[i][1] * 1000)].export(
            config.storage.audio_dir / str(file_id), format="mp3"
        )
        files.append(file_id)

    return files


def split_silence(
    file: str, max_interval: float = 30, cutoff_ratio: float = 0.05
) -> Tuple[List[UUID], List[Tuple[int, int]]]:
    """
    Splits the audio file into segments of some length
    Only cuts on silence, never cuts words
    Leaves a 50 ms buffer around every segment
    :param file: the path to the file to be split
    :param max_interval: the maximum length of a segment
    :param cutoff_ratio: the percentage of max volume at which a segment is considered "silent"
    :return: the list of the UUIDs of all the cut-up segments and the intervals at which they were cut
    """

    # Creating the pydub.AudioSegment and preparing some variables for audio processing
    audio: AudioSegment = AudioSegment.from_file(file, file[file.rfind(".") + 1 :])  # type: ignore
    max_dbfs = audio.max_dBFS
    noise_level = fraction_to_dbfs(cutoff_ratio * dbfs_to_fraction(max_dbfs))

    # Detecting the silence
    silence_chunks = silence.detect_silence(
        audio, min_silence_len=100, silence_thresh=noise_level
    )
    audio_intervals = []

    # Padding the audio if it does not begin or end with silence
    max_interval *= 1000
    if silence_chunks[0][0] != 0:
        audio = AudioSegment.silent(100) + audio
        silence_chunks = [
            (silence_chunks[i][0] + 100, silence_chunks[i][1] + 100)
            for i in range(len(silence_chunks))
        ]
        silence_chunks.insert(0, (0, 100))
    if silence_chunks[-1][1] != len(audio):
        silence_chunks.append((len(audio), len(audio) + 100))
        audio = audio + AudioSegment.silent(100)
    new_beg = silence_chunks[0][1] - 50

    # Accumulating words until we reach the threshold
    for i in range(1, len(silence_chunks)):
        if 50 + silence_chunks[i][0] - new_beg > max_interval:
            audio_intervals.append((new_beg, silence_chunks[i - 1][0] + 50))
            new_beg = silence_chunks[i - 1][1] - 50

    audio_intervals.append((new_beg, silence_chunks[-1][0] + 50))

    # Split by counted intervals and return the result
    return (
        split_audio(audio, [(i[0] / 1000, i[1] / 1000) for i in audio_intervals]),
        audio_intervals,
    )

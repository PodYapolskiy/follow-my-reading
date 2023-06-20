from pydub import AudioSegment
from os import path


def split(file, intervals):
    # file is the path to the file to be split
    # intervals is the set of intervals to be returned in format of [(begin(seconds), length(seconds)),]
    # returns the absolute path to where the split segments were stored

    store_path = "out"

    audio = AudioSegment.from_file(file, file[file.find(".") + 1])
    for i in range(len(intervals)):
        audio[int(intervals[i][0]*1000):
              int((intervals[i][0] + intervals[i][1])*1000)].export(f"{store_path}/{i}.mp3", format="mp3")

    return path.abspath(store_path)



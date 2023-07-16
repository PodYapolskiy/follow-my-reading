![Pipeline](https://gitlab.pg.innopolis.university/a.kudryavtsev/follow-my-reading/badges/main/pipeline.svg)
![Packaging: poetry](https://img.shields.io/badge/packaging-poetry-cyan.svg)
![Linting: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v1.json)
![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)

# Follow My Reading :blue_book:

Follow My Reading provides a API service for our users to upload an image and audio of their reading session, and our service checks whether there are any mistakes in pronunciation in the audio.


### Here's how it works :gear:
- :sunrise: users can take a photo of the page
- :book: read the page aloud
- :microphone: record their audio
- :arrow_up: upload image and audio files to sever
- :gear: :park: server can process image
- :gear: :musical_note: server can process audio
- :musical_note:: arrows_counterclockwise: :frame_photo: server can compare audio against image
- :musical_note: :arrows_counterclockwise: :page_facing_up: server can compare audio against text
- :musical_note: :arrow_right: server can extract audio segments with requested phrases


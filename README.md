![Pipeline](https://gitlab.pg.innopolis.university/a.kudryavtsev/follow-my-reading/badges/main/pipeline.svg)
![Packaging: poetry](https://img.shields.io/badge/packaging-poetry-cyan.svg)
![Linting: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v1.json)
![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)

# Follow My Reading :blue_book:

Follow My Reading provides a **API service** for our users to upload an image and audio of their reading session, and our service checks whether there are any mistakes in pronunciation in the audio.


## Here's how it works :gear:
:sunrise: users can take **a photo of the page**

:book: read the page **aloud**

:microphone: record their **audio**

:arrow_up: **upload image** and audio files to sever

:park: server can **process image**

:musical_note: server can **process audio**

:frame_photo: server can **compare audio against image**

:page_facing_up: server can **compare audio against text**

:arrow_double_down: server can **extract audio** segments with requested phrases

## Full list if features
Full list of Features:

:white_check_mark: Image and audio upload

:white_check_mark: Audio Processing

:white_check_mark: Splitting audio by words or by phrases

:white_check_mark: Image Processing

:white_check_mark: Reporting text coordinates on the image

:white_check_mark: Comparing audio and image

:white_check_mark: Comparing audio and text

:white_check_mark: Extracting audio by given phrases

:white_check_mark: Plugin Support

:white_check_mark: Multi-language support

:white_check_mark: Distributed computing using Task System

:white_check_mark: Authentication

## Documentation

We **host the documentation** for our API here: [:globe_with_meridians: Gitlab Pages](http://antonkudryavtsevdoem.fvds.ru/docs#/), where you will find all the information you need to use our API effectively.

In addition to the API documentation, we also have **a detailed wiki** that explains everything in detail: [:page_facing_up: Project Wiki](https://gitlab.pg.innopolis.university/a.kudryavtsev/follow-my-reading/-/wikis/home) . This resource provides more comprehensive information, so feel free to take a deep dive and explore the different sections.

## License
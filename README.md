![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Packaging: poetry](https://img.shields.io/badge/packaging-poetry-cyan.svg)
![Linting: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v1.json)
![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)

# Follow My Reading 📘

Follow My Reading provides a **API service** for our users to upload an image and audio of their reading session, and our service checks whether there are any mistakes in pronunciation in the audio.

## Here's how it works ⚙️

🌅 users can take **a photo of the page**

📖 read the page **aloud**

🎤 record their **audio**

⬆️ **upload image** and audio files to sever

🏞️ server can **process image**

🎵 server can **process audio**

🖼️ server can **compare audio against image**

📄 server can **compare audio against text**

⏬ server can **extract audio** segments with requested phrases

## Frameworks and technologies

- [⚡️ FastAPI](https://fastapi.tiangolo.com/)

> FastAPI is a modern, fast (high-performance) web framework for building APIs with Python 3.6+ based on standard Python type hints, making it easy to write and maintain complex APIs in a fast and scalable way.

- [🗄 Redis](https://redis.io/)

> Redis is an open source, in-memory data structure store, used as a database, cache, and message broker, with support for a wide range of data structures and features that make it highly versatile and efficient.

- [⚙️ Huey](https://huey.readthedocs.io/en/latest/)

> Huey is a lightweight task queue for Python that allows for easy integration with Redis and asynchronous processing of tasks in distributed systems.

## Full list of features ✨

✅ Image and audio upload

✅ Audio Processing

✅ Splitting audio by words or by phrases

✅ Image Processing

✅ Reporting text coordinates on the image

✅ Comparing audio and image

✅ Comparing audio and text

✅ Extracting audio by given phrases

✅ Plugin Support

✅ Multi-language support

✅ Distributed computing using Task System

✅ Authentication

## Documentation 📄

We **host the documentation** for our API here: [🌐 Gitlab Pages](http://antonkudryavtsevdoem.fvds.ru/docs#/), where you will find all the information you need to use our API effectively.

In addition to the API documentation, we also have **a detailed wiki** that explains everything in detail: [📄 Project Wiki](https://gitlab.pg.innopolis.university/a.kudryavtsev/follow-my-reading/-/wikis/home). This resource provides more comprehensive information, so feel free to take a deep dive and explore the different sections.

## Team 👥

- @a.kudryavtsev
- @a.soldatov
- @i.sannikov
- @f.smirnov
- @l.novikov

## License 📃

This project is licensed under the terms of the **MIT License**.

[MIT License](https://opensource.org/licenses/MIT)

# Follow My Reading

[[_TOC_]]

# Overview
Follow My Reading is a game-changer for individuals who may struggle with proper pronunciation while reading. Follow My Reading provides a API service for our users to upload an image and audio of their reading session, and our service checks whether there are any mistakes in pronunciation in the audio.

Here's how it works - users can take a photo of the text, read it aloud, and record their audio simultaneously using their device. Our platform reviews the audio against the text on the image and provides feedback on areas that need improvement. Our technology uses several deep neural network models to detect mispronunciation of words.

Moreover, the "Follow My Reading" project has been designed to be highly customizable and easily configurable to meet the needs of different users and applications. The system administrator has the flexibility to add or remove models for audio and image processing as needed, making it a very versatile system.

Adding or removing models from the platform can be accomplished quickly thanks to the plugin system. This approach allows administrator to create a custom audio or image processing plugin. Thus, the plugin system allows administrator to add custom models, extend the functionality of existing models, integrate third-party models, or even train their own processing models making "Follow My Reading" an even more powerful

## Documentation Overview
- [Overview](#Overview)
  > This section provides an introduction to the product and its features, along with a summary of the content and structure of the documentation.
- [Installation](#Installation)
  > This section covers the steps required to install the product, including prerequisites, system requirements, installation options, and troubleshooting tips. This section may also include information on how to update or uninstall the product.
- [Deployment](#Deployment)
  > This section provides guidance on deploying the product in different environments or scenarios, such as on-premise, cloud, or hybrid deployments. It may cover topics such as scaling, fault-tolerance, security, and monitoring.
- [Plugins](#Plugins)
  > This section explains how to and manage plugins, which provide additional functionalities to the product. This include information on how to create or customize plugins, as well as best practices for using plugins effectively.
- [Algorithms](#Algorithms)
  > This section explains algorithms that are used for the product to work. This include descriptions of algorithms, what they accept and what they return.
- [API](#API)
  > This section documents the product's API and provides guidance on how to use it. This may include information on supported protocols, authentication, rate limiting, and error handling. Sample code snippets and use cases may also be provided.
- [Advanced](#Advanced)
  > This section covers more advanced topics, such as performance optimization, customization, integration with other systems, and troubleshooting complex issues. This section also include an explanation of the task system functionality.

## Full list of Features
- ✅ Image and audio upload
- ✅ Audio Processing
- ✅ Splitting audio by words or by phrases
- ✅ Image Processing
- ✅ Reporting text coordinates on the image
- ✅ Comparing audio and image
- ✅ Comparing audio and text
- ✅ Extracting audio by given phrases
- ✅ Plugin Support
- ✅ Distributed computing using Task System
- ✅ Authentication

# Installation
Before locally using Follow My Reading, there are a few prerequisites that need to be installed first.
## Prerequisites

### 1. Install Python 3.10
Python is required for the installation of Follow My Reading. If Python is not already installed on your device, download and install it from the official [Python website](https://www.python.org/downloads).

### 2. Install pip
Pip is a package manager for Python packages. It allows you to install and manage additional packages that are not included with Python by default. To install Pip, follow the instructions below:
- For Windows:
```cmd
py -m ensurepip --upgrade
```
- For Linux/MacOS:
```bash
python -m ensurepip --upgrade
```
### 3. Install Poetry
Poetry is a Python packaging and dependency management tool. You can install it by running the following command:
```bash
pip install poetry
```
### 4. Get the source code:
Once you have the access to the code, to get it, use the following command:
```bash
git clone https://gitlab.pg.innopolis.university/a.kudryavtsev/follow-my-reading.git
```

### 5. Install project dependencies
To install all project dependencies, use the following command
```bash
poetry install
```

These steps will ensure that you have everything required to be able to install and use Follow My Reading.

### 6. \[Optional\] Model Dependencies
Several models require additional steps to set up.
#### Tesseract
- [Instructions for installing Tesseract.](https://github.com/tesseract-ocr/tesseract)

- [Instructions for installing Tessdata.](https://github.com/tesseract-ocr/tessdata)

# Deployment

Follow My Reading can be deployed in several ways depending on your requirements. Below are instructions for deploying Follow My Reading in different ways.

## Stand-alone
If you want to run Follow My Reading as a stand-alone Docker container, you can run the following command:
```bash
make standalone
```
This will build and run the Follow My Reading Docker container.

## Launch
If you want to run Follow My Reading locally with Redis and Huey, you need to run the following commands:
- Run the Redis server:
```
redis-server
```
- Run the Huey consumer:
```
huey_consumer.py core.task_system.scheduler -n -k thread
```
- Run the server:
```
uvicorn main:app
```

## Scalability
Follow My Reading can be scaled horizontally by running multiple Huey consumers with the following command:
```
huey_consumer.py core.task_system.scheduler -n -k thread -w NUMBER
```
Where `NUMBER` is the number of workers you want to run. You can run this command on multiple machines to run a worker on each of them, as long as they are connected to Redis.

> NOTE! Right now executing task on multiple machines is unstable

# Plugins
# Quick Start
## First Plugin
Plugins in our system are described as Python files in the /plugins directory. There are several requirements for the format of these plugins. To implement a new plugin, create a file with a name that ends in _plugin.py. In this file, you should include the following imports:

For Image processing models:
```python
from core.plugins import (
    ImageProcessingResult,
    ImageTextBox,
    Point,
    Rectangle,
    register_plugin,
)
```


For Audio processing models:
```python
from core.plugins import AudioChunk, AudioProcessingResult, register_plugin
```

The `register_plugin` function is a decorator that you should use to register your custom plugin. This function takes a single parameter which is the class of your plugin.

## Image Processing Example
Here is an example of how to create and register a custom plugin for image processing:

```python
import easyocr

from core.plugins import (
    ImageProcessingResult,
    ImageTextBox,
    Point,
    Rectangle,
    register_plugin,
)


@register_plugin
class EnArEasyOCRPlugin:
    name = "en_ar_easyocr"
    description = (
        "An open source library for certain languages and alphabets,"
        "mainly used for working with text on an image"
    )

    # List of supported languages can be found here: https://www.jaided.ai/easyocr/
    languages = ["en", "ar"]

    reader = easyocr.Reader(languages, gpu=False)

    @staticmethod
    def process_image(filename: str) -> ImageProcessingResult:
        model_response = EnArEasyOCRPlugin.reader.readtext(filename)
        boxes = []
        for coordinates, text, _ in model_response:
            lt, rt, rb, lb = coordinates
            boxes.append(
                ImageTextBox(
                    text=text,
                    coordinates=Rectangle(
                        left_top=Point(x=lt[0], y=lt[1]),
                        right_top=Point(x=rt[0], y=rt[1]),
                        right_bottom=Point(x=rb[0], y=rb[1]),
                        left_bottom=Point(x=lb[0], y=lb[1]),
                    ),
                )
            )
        result_text = " ".join(map(lambda x: x[1], model_response))

        return ImageProcessingResult(text=result_text, boxes=boxes)
```

## Audio Processing Example
And here is an example of how to create and register a custom plugin for audio processing:

```python
import whisper

from core.plugins import AudioChunk, AudioProcessingResult, register_plugin


@register_plugin
class WhisperPlugin:
    name = "whisper"
    languages = ["en", "ru", "ar"]
    description = "Robust Speech Recognition via Large-Scale Weak Supervision By OpenAI"

    model = whisper.load_model("base")  # large-v2

    @staticmethod
    def process_audio(filename: str) -> AudioProcessingResult:
        model_response = WhisperPlugin.model.transcribe(filename)
        chunks = [
            AudioChunk(start=seg["start"], end=seg["end"], text=seg["text"])
            for seg in model_response["segments"]
        ]

        return AudioProcessingResult(text=model_response["text"], segments=chunks)
```

# Requirements

In our system, each plugin file must be named in the format `*_plugin.py` and located in the `/plugins` directory. Each plugin must also contain the following static variables:
- `name`: A string that specifies the name of the plugin.
- `languages`: A list of strings specifying the natural languages that the plugin can process.
- `description`: A string that provides a description of the plugin.

Additionally, each plugin must implement one of the following static methods:
- `process_audio(filename: str)`: Must accept an argument of type string and return an object of type AudioProcessingResult.
- `process_image(filename: str)`: Must accept an argument of type string and return an object of type ImageProcessingResult.

# Algorithms
# Audio Algorithms
## `dbfs_to_fraction`
The `dbfs_to_fraction` function accepts a decibel value relative to full scale (dbfs) and returns the corresponding fraction of the maximum volume as a float.

## `fraction_to_dbfs`
The `fraction_to_dbfs` function accepts a fraction of the maximum volume and returns the corresponding decibels relative to full scale (dbfs) as a float.

## `split_audio`
The `split_audio` function accepts the path to an audio file or a pydub AudioSegment object and a list of tuples representing the timestamps for the beginning and end of each desired segment (in seconds). The function returns the UUIDs of the cut-up files in the order they appeared in the intervals.

## `split_silence`
The `split_silence` function accepts the path to an audio file, the maximum length of a desired segment (in seconds), and the percentage of the maximum volume at which a segment is considered "silent". The function cuts the file only by silence, not by words, and adds a 50 ms buffer around each segment. The function returns a list of the UUIDs of all the cut-up segments and the intervals at which they were cut.

# Text Algorithms
## `match_words`
The `match_words` function accepts two texts and returns a list of changes that need to be made to the first text in order to get the second one. The comparison takes place using whole words, and the function returns the list of changes in the following format: Tuple(Index in the first text where the difference was found,  The segment of the first text which is to be removed, The segment of the second text which is to be substituted in).

## `match_phrases`
`match_phrases` is a function that takes in two arguments, `phrases` and `text`. `phrases` is a list of phrases or string fragments to be checked against `text`, which is the correct text. It returns a list of error tuples for each phrase in the `phrases` list, indicating the index at which the error occurred, the incorrect phrase, and the correct phrase.

The function first prepares the input texts by ignoring capital letters and non-letter symbols. It then uses levenshtein distance to calculate the full answer between the `phrases` and `text`. Finally, it cross-references the indices in the full answer to distribute the errors by phrases.


## `find_phrases`
`find_phrases` is a function that takes in three arguments, `phrases`, `to_find`, and `margin` (default 1.05). `phrases` is a list of phrases; `to_find` is the piece of text to be found within the `phrases`. It returns a list of indices of the phrases in which the text appears in.

The function first prepares the input `to_find` and `phrases` to ignore multiple spaces and non-letter symbols by calling on the helper function `__prep_text`. It then computes the size of a window to compare to the text and finds the window that best fits the string via the `__match_symbols` helper function.

The function then trims the window to exclude unnecessary symbols (trims using full words) and transforms the indices from the prepared text to initial text. Lastly, it iterates through the phrases to compute the final answer.

# API

<h1 id="fastapi">FastAPI v0.1.0</h1>

> Scroll down for code samples, example requests and responses. Select a language for code samples from the tabs above or the mobile navigation menu.

# Authentication

- oAuth2 authentication. 

    - Flow: password

    - Token URL = [/v1/auth/token](/v1/auth/token)

|Scope|Scope Description|
|---|---|

<h1 id="fastapi-audio">audio</h1>

## The endpoint /upload allows clients to upload audio files and returns a unique file ID.

<a id="opIdupload_audio_file_v1_audio_upload_post"></a>

> Code samples

`POST /v1/audio/upload`

The endpoint validates file based on
[MIME types specification](https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Common_types).
The endpoint converts audio file into `.mp3` format.

Parameters:
- **upload_file**: The audio file to upload

List of the most important allowed extensions:
- .acc
- .mp3
- .m4a
- .oga, .ogv
- .ogg
- .opus
- .wav

> Body parameter

```yaml
upload_file: string

```

<h3 id="the-endpoint-/upload-allows-clients-to-upload-audio-files-and-returns-a-unique-file-id.-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|[Body_upload_audio_file_v1_audio_upload_post](#schemabody_upload_audio_file_v1_audio_upload_post)|true|none|
|» upload_file|body|string(binary)|true|none|

> Example responses

> 200 Response

```json
{
  "file_id": "8a0cfb4f-ddc9-436d-91bb-75133c583767"
}
```

> 422 Response

```json
{
  "detail": "Only audio files uploads are allowed"
}
```

<h3 id="the-endpoint-/upload-allows-clients-to-upload-audio-files-and-returns-a-unique-file-id.-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|The file is uploaded successfully|[UploadFileResponse](#schemauploadfileresponse)|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|The file was not sent or the file has unallowed extension|None|

<h3 id="the-endpoint-/upload-allows-clients-to-upload-audio-files-and-returns-a-unique-file-id.-responseschema">Response Schema</h3>

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2PasswordBearer
</aside>

## The endpoint `/download` allows to download audio file by given uuid.

<a id="opIddownload_audio_file_v1_audio_download_get"></a>

> Code samples

`GET /v1/audio/download`

The endpoint `/download` takes a file UUID as input, checks if the file exists in the
audio directory, and returns the file as bytes (`.mp3` format). If file does not exist, returns 404 HTTP response code

Responses:
- 200, file bytes (`.mp3` format)

<h3 id="the-endpoint-`/download`-allows-to-download-audio-file-by-given-uuid.-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|file|query|string(uuid)|true|none|

> Example responses

> 404 Response

```json
{
  "detail": "File not found"
}
```

> 422 Response

```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string"
    }
  ]
}
```

<h3 id="the-endpoint-`/download`-allows-to-download-audio-file-by-given-uuid.-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|None|
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|The specified file was not found.|None|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|

<h3 id="the-endpoint-`/download`-allows-to-download-audio-file-by-given-uuid.-responseschema">Response Schema</h3>

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2PasswordBearer
</aside>

## The endpoint /models returns available (loaded) audio models.

<a id="opIdget_audio_processing_models_v1_audio_models_get"></a>

> Code samples

`GET /v1/audio/models`

Returns list of models, which are loaded into the worker and available for usage.

> Example responses

> 200 Response

```json
{
  "models": [
    {
      "name": "string",
      "languages": [
        "string"
      ],
      "description": "string"
    }
  ]
}
```

<h3 id="the-endpoint-/models-returns-available-(loaded)-audio-models.-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|List of available models|[ModelsDataReponse](#schemamodelsdatareponse)|

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2PasswordBearer
</aside>

## The endpoint `/process/task` creates an audio processing task based on the given request parameters.

<a id="opIdprocess_audio_v1_audio_process_task_post"></a>

> Code samples

`POST /v1/audio/process/task`

Parameters:
- **audio_file**: an uuid of file to process
- **audio_model**: an audio processing model name (check '_/models_' for available models)

Responses:
- 404, No such audio file available
- 404, No such audio model available

> Body parameter

```json
{
  "audio_file": "732b10bd-0006-4780-8f48-4319d2791290",
  "audio_model": "string"
}
```

<h3 id="the-endpoint-`/process/task`-creates-an-audio-processing-task-based-on-the-given-request-parameters.-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|[AudioProcessingRequest](#schemaaudioprocessingrequest)|true|none|
|» audio_file|body|string(uuid)|true|none|
|» audio_model|body|string|true|none|

> Example responses

> 200 Response

```json
{
  "task_id": "736fde4d-9029-4915-8189-01353d6982cb"
}
```

> 404 Response

```json
{
  "detail": "No such audio file available"
}
```

<h3 id="the-endpoint-`/process/task`-creates-an-audio-processing-task-based-on-the-given-request-parameters.-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Task was successfully created and scheduled|[TaskCreateResponse](#schemataskcreateresponse)|
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|The specified file or model was not found.|None|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|

<h3 id="the-endpoint-`/process/task`-creates-an-audio-processing-task-based-on-the-given-request-parameters.-responseschema">Response Schema</h3>

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2PasswordBearer
</aside>

## The endpoint `/process/result` retrieves the result of an audio
processing task from task system and returns it.

<a id="opIdget_response_v1_audio_process_result_get"></a>

> Code samples

`GET /v1/audio/process/result`

Responses:
- 200, returns a processing result in the format:
```js
{
    "text": "string", // total extracted text
    "segments": [ // list of audio segments
        {
        "start": 0.0, // absolute timecode (in seconds) of the beginning of the segment
        "end": 10.0,  // absolute timecode (in seconds) of the beginning of the segment
        "text": "string", // text, which was extracted from the segment
        "file": "3fa85f64-5717-4562-b3fc-2c963f66afa6" // file uuid of the audio segment (for downloading)
        }
    ]
}
```
- 406, is impossible to get task result (task does not exist or it has not finished yet).
- 422, if the task was not created as audio processing task

<h3 id="the-endpoint-`/process/result`-retrieves-the-result-of-an-audio
processing-task-from-task-system-and-returns-it.-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|task_id|query|string(uuid)|true|none|

> Example responses

> 200 Response

```json
{
  "text": "string",
  "segments": [
    {
      "start": 0,
      "end": 0,
      "text": "string",
      "file": "00bd29cf-1ab3-4825-b15f-d80a4a0e1cbb"
    }
  ]
}
```

> 406 Response

```json
{
  "detail": "The job is non-existent or not done"
}
```

> 422 Response

```json
{
  "detail": "There is no such audio processing task"
}
```

<h3 id="the-endpoint-`/process/result`-retrieves-the-result-of-an-audio
processing-task-from-task-system-and-returns-it.-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|[AudioProcessingResponse](#schemaaudioprocessingresponse)|
|406|[Not Acceptable](https://tools.ietf.org/html/rfc7231#section-6.5.6)|It is impossible to get task result (task does not exist or it has not finished yet).|None|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|The specified task is not audio processing task.|None|

<h3 id="the-endpoint-`/process/result`-retrieves-the-result-of-an-audio
processing-task-from-task-system-and-returns-it.-responseschema">Response Schema</h3>

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2PasswordBearer
</aside>

## The endpoint `/extract/task` extract specified phrases from given audio 
file using specified given audio model

<a id="opIdextract_text_from_audio_v1_audio_extract_task_post"></a>

> Code samples

`POST /v1/audio/extract/task`

Parameters:
- **audio_file**: an uuid of file to process
- **audio_model**: an audio processing model name (check '_/models_' for available models)

Responses:
- 404, No such audio file available
- 404, No such audio model available

> Body parameter

```json
{
  "audio_file": "732b10bd-0006-4780-8f48-4319d2791290",
  "audio_model": "string",
  "phrases": [
    "string"
  ]
}
```

<h3 id="the-endpoint-`/extract/task`-extract-specified-phrases-from-given-audio-
file-using-specified-given-audio-model-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|[AudioExtractPhrasesRequest](#schemaaudioextractphrasesrequest)|true|none|
|» audio_file|body|string(uuid)|true|none|
|» audio_model|body|string|true|none|
|» phrases|body|[string]|true|none|

> Example responses

> 200 Response

```json
{
  "task_id": "736fde4d-9029-4915-8189-01353d6982cb"
}
```

> 404 Response

```json
{
  "detail": "No such audio file available"
}
```

<h3 id="the-endpoint-`/extract/task`-extract-specified-phrases-from-given-audio-
file-using-specified-given-audio-model-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Task was successfully created and scheduled|[TaskCreateResponse](#schemataskcreateresponse)|
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|The specified file or model was not found.|None|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|

<h3 id="the-endpoint-`/extract/task`-extract-specified-phrases-from-given-audio-
file-using-specified-given-audio-model-responseschema">Response Schema</h3>

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2PasswordBearer
</aside>

## The endpoint `/extract/result` retrieves the result of an audio
extracting task from task system and returns it.

<a id="opIdget_extracted_results_v1_audio_extract_result_get"></a>

> Code samples

`GET /v1/audio/extract/result`

<h3 id="the-endpoint-`/extract/result`-retrieves-the-result-of-an-audio
extracting-task-from-task-system-and-returns-it.-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|task_id|query|string(uuid)|true|none|

> Example responses

> 200 Response

```json
{
  "data": [
    {
      "audio_segment": {
        "start": 0,
        "end": 0,
        "text": "string",
        "file": "00bd29cf-1ab3-4825-b15f-d80a4a0e1cbb"
      },
      "found": true,
      "phrase": "string"
    }
  ]
}
```

> 406 Response

```json
{
  "detail": "The job is non-existent or not done"
}
```

> 422 Response

```json
{
  "detail": "There is no such audio extraction task"
}
```

<h3 id="the-endpoint-`/extract/result`-retrieves-the-result-of-an-audio
extracting-task-from-task-system-and-returns-it.-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|[AudioExtractPhrasesResponse](#schemaaudioextractphrasesresponse)|
|406|[Not Acceptable](https://tools.ietf.org/html/rfc7231#section-6.5.6)|It is impossible to get task result (task does not exist or it has not finished yet).|None|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|The specified task is not audio extraction task.|None|

<h3 id="the-endpoint-`/extract/result`-retrieves-the-result-of-an-audio
extracting-task-from-task-system-and-returns-it.-responseschema">Response Schema</h3>

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2PasswordBearer
</aside>

<h1 id="fastapi-image">image</h1>

## The endpoint /upload allows clients to upload image files and returns a unique file ID.

<a id="opIdupload_image_v1_image_upload_post"></a>

> Code samples

`POST /v1/image/upload`

The endpoint validates file based on
[MIME types specification](https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Common_types).
The endpoint converts image file into .png format.

Parameters:
- **upload_file**: The file to upload

Allowed extension:
- .avif
- .bmp
- .gif
- .ico
- .jpeg, .jpg
- .png
- .svg
- .tif, .tiff
- .webp

> Body parameter

```yaml
upload_file: string

```

<h3 id="the-endpoint-/upload-allows-clients-to-upload-image-files-and-returns-a-unique-file-id.-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|[Body_upload_image_v1_image_upload_post](#schemabody_upload_image_v1_image_upload_post)|true|none|
|» upload_file|body|string(binary)|true|none|

> Example responses

> 200 Response

```json
{
  "file_id": "8a0cfb4f-ddc9-436d-91bb-75133c583767"
}
```

> 422 Response

```json
{
  "detail": "Only image files uploads are allowed"
}
```

<h3 id="the-endpoint-/upload-allows-clients-to-upload-image-files-and-returns-a-unique-file-id.-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|The file is uploaded successfully|[UploadFileResponse](#schemauploadfileresponse)|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|The file was not sent or the file has unallowed extension|None|

<h3 id="the-endpoint-/upload-allows-clients-to-upload-image-files-and-returns-a-unique-file-id.-responseschema">Response Schema</h3>

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2PasswordBearer
</aside>

## The endpoint `/download` allows to download audio file by given uuid.

<a id="opIddownload_image_file_v1_image_download_get"></a>

> Code samples

`GET /v1/image/download`

The endpoint `/download` takes a file UUID as input, checks if the file exists in the
image directory, and returns the file as bytes. If file does not exist, returns 404 HTTP response code

Responses:
- 200, file bytes

<h3 id="the-endpoint-`/download`-allows-to-download-audio-file-by-given-uuid.-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|file|query|string(uuid)|true|none|

> Example responses

> 404 Response

```json
{
  "detail": "File not found"
}
```

> 422 Response

```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string"
    }
  ]
}
```

<h3 id="the-endpoint-`/download`-allows-to-download-audio-file-by-given-uuid.-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|None|
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|The specified file was not found.|None|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|

<h3 id="the-endpoint-`/download`-allows-to-download-audio-file-by-given-uuid.-responseschema">Response Schema</h3>

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2PasswordBearer
</aside>

## The endpoint /models returns available (loaded) image models.

<a id="opIdget_models_v1_image_models_get"></a>

> Code samples

`GET /v1/image/models`

Returns list of models, which are loaded into the worker and available for usage.

> Example responses

> 200 Response

```json
{
  "models": [
    {
      "name": "string",
      "languages": [
        "string"
      ],
      "description": "string"
    }
  ]
}
```

<h3 id="the-endpoint-/models-returns-available-(loaded)-image-models.-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|List of available models|[ModelsDataReponse](#schemamodelsdatareponse)|

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2PasswordBearer
</aside>

## The endpoint `/process/task` creates an image processing task based on the given request parameters.

<a id="opIdprocess_image_v1_image_process_task_post"></a>

> Code samples

`POST /v1/image/process/task`

Parameters:
- **image_file**: an uuid of file to process
- **image_model**: an image processing model name (check '_/models_' for available models)

Responses:
- 404, No such image file available
- 404, No such image model available

> Body parameter

```json
{
  "image_file": "89f23c23-fe12-4935-b746-3bbc447c7a72",
  "image_model": "string"
}
```

<h3 id="the-endpoint-`/process/task`-creates-an-image-processing-task-based-on-the-given-request-parameters.-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|[ImageProcessingRequest](#schemaimageprocessingrequest)|true|none|
|» image_file|body|string(uuid)|true|none|
|» image_model|body|string|true|none|

> Example responses

> 200 Response

```json
{
  "task_id": "736fde4d-9029-4915-8189-01353d6982cb"
}
```

> 404 Response

```json
{
  "detail": "No such image file available"
}
```

<h3 id="the-endpoint-`/process/task`-creates-an-image-processing-task-based-on-the-given-request-parameters.-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Task was successfully created and scheduled|[TaskCreateResponse](#schemataskcreateresponse)|
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|The specified file or model was not found.|None|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|

<h3 id="the-endpoint-`/process/task`-creates-an-image-processing-task-based-on-the-given-request-parameters.-responseschema">Response Schema</h3>

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2PasswordBearer
</aside>

## The endpoint `/process/result` retrieves the result of an image
processing task from task system and returns it.

<a id="opIdget_response_v1_image_process_result_get"></a>

> Code samples

`GET /v1/image/process/result`

Responses:
- 200, returns a processing result in the format:
```js
{
    "text": "string", // total extracted text
    "boxes": [ // list of boxes with text
        {
        "text": "string", // text, which was extracted from the box
        "coordinates": { // coordinates of the box on image
            "left_top": { // four points defining the rectangle
            "x": 0,
            "y": 0
            },
            "right_top": {
            "x": 0,
            "y": 0
            },
            "left_bottom": {
            "x": 0,
            "y": 0
            },
            "right_bottom": {
            "x": 0,
            "y": 0
            }
        }
        }
    ]
}
```
- 406, is impossible to get task result (task does not exist or it has not finished yet).
- 422, if the task was not created as audio processing task

<h3 id="the-endpoint-`/process/result`-retrieves-the-result-of-an-image
processing-task-from-task-system-and-returns-it.-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|task_id|query|string(uuid)|true|none|

> Example responses

> 200 Response

```json
{
  "text": "string",
  "boxes": [
    {
      "text": "string",
      "coordinates": {
        "left_top": {
          "x": 0,
          "y": 0
        },
        "right_top": {
          "x": 0,
          "y": 0
        },
        "left_bottom": {
          "x": 0,
          "y": 0
        },
        "right_bottom": {
          "x": 0,
          "y": 0
        }
      }
    }
  ]
}
```

> 406 Response

```json
{
  "detail": "The job is non-existent or not done"
}
```

> 422 Response

```json
{
  "detail": "There is no such image processing task"
}
```

<h3 id="the-endpoint-`/process/result`-retrieves-the-result-of-an-image
processing-task-from-task-system-and-returns-it.-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|[ImageProcessingResponse](#schemaimageprocessingresponse)|
|406|[Not Acceptable](https://tools.ietf.org/html/rfc7231#section-6.5.6)|It is impossible to get task result (task does not exist or it has not finished yet).|None|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|The specified task is not image processing task.|None|

<h3 id="the-endpoint-`/process/result`-retrieves-the-result-of-an-image
processing-task-from-task-system-and-returns-it.-responseschema">Response Schema</h3>

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2PasswordBearer
</aside>

<h1 id="fastapi-auth">auth</h1>

## The endpoint `/register` registers a new user by storing their username, password, email, and
    full name in a Redis database.

<a id="opIdregister_user_v1_auth_register_put"></a>

> Code samples

`PUT /v1/auth/register`

Parameters:
- **username**: The "username: parameter is a string representing the username of the user being registered
- **password**: The "password" parameter is a string that represents the user's password
- **email**: The "email" parameter is an optional string that represents the email address of the user
- **full_name**: The "full_name" parameter is an optional parameter that represents the full name of the user

<h3 id="the-endpoint-`/register`-registers-a-new-user-by-storing-their-username,-password,-email,-and
----full-name-in-a-redis-database.-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|username|query|string|true|none|
|password|query|string|true|none|
|email|query|string|false|none|
|full_name|query|string|false|none|

> Example responses

> 200 Response

```json
{
  "text": "string"
}
```

> 422 Response

```json
{
  "detail": "Username is already taken"
}
```

<h3 id="the-endpoint-`/register`-registers-a-new-user-by-storing-their-username,-password,-email,-and
----full-name-in-a-redis-database.-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|[RegisterResponse](#schemaregisterresponse)|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|The specified username is already taken|None|

<h3 id="the-endpoint-`/register`-registers-a-new-user-by-storing-their-username,-password,-email,-and
----full-name-in-a-redis-database.-responseschema">Response Schema</h3>

<aside class="success">
This operation does not require authentication
</aside>

## The endpoint `/token` handles the login process and returns an
access token for the authenticated user.

<a id="opIdlogin_for_access_token_v1_auth_token_post"></a>

> Code samples

`POST /v1/auth/token`

Parameters:
- **username** - unique username, which the client has provided while registering
- **password** - client's password

Responses:
- 401, incorrect username or password
- 200, token

> Body parameter

```yaml
grant_type: string
username: string
password: string
scope: ""
client_id: string
client_secret: string

```

<h3 id="the-endpoint-`/token`-handles-the-login-process-and-returns-an
access-token-for-the-authenticated-user.-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|[Body_login_for_access_token_v1_auth_token_post](#schemabody_login_for_access_token_v1_auth_token_post)|true|none|
|» grant_type|body|string|false|none|
|» username|body|string|true|none|
|» password|body|string|true|none|
|» scope|body|string|false|none|
|» client_id|body|string|false|none|
|» client_secret|body|string|false|none|

> Example responses

> 200 Response

```json
{
  "access_token": "string",
  "token_type": "string"
}
```

> 401 Response

```json
{
  "detail": "Incorrect username or password"
}
```

<h3 id="the-endpoint-`/token`-handles-the-login-process-and-returns-an
access-token-for-the-authenticated-user.-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|[Token](#schematoken)|
|401|[Unauthorized](https://tools.ietf.org/html/rfc7235#section-3.1)|Incorrect username or password.|None|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|

<h3 id="the-endpoint-`/token`-handles-the-login-process-and-returns-an
access-token-for-the-authenticated-user.-responseschema">Response Schema</h3>

<aside class="success">
This operation does not require authentication
</aside>

## The endpoint `/users/me` returns the current user.

<a id="opIdread_users_me_v1_auth_users_me_get"></a>

> Code samples

`GET /v1/auth/users/me`

> Example responses

> 200 Response

```json
{
  "username": "string",
  "email": "string",
  "full_name": "string",
  "disabled": true
}
```

> 400 Response

```json
{
  "detail": "Inactive user"
}
```

> 401 Response

```json
{
  "detail": "Could not validate credentials"
}
```

<h3 id="the-endpoint-`/users/me`-returns-the-current-user.-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|[User](#schemauser)|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|User is inactive|None|
|401|[Unauthorized](https://tools.ietf.org/html/rfc7235#section-3.1)|Could not validate credentials|None|

<h3 id="the-endpoint-`/users/me`-returns-the-current-user.-responseschema">Response Schema</h3>

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2PasswordBearer
</aside>

<h1 id="fastapi-comparison">comparison</h1>

## The endpoint `/audio/image/task` creates a task to compare an audio against image file using specified
    models and returns the task ID.

<a id="opIdcompare_audio_to_image_v1_comparison_audio_image_task_post"></a>

> Code samples

`POST /v1/comparison/audio/image/task`

Parameters:
- **audio_file**: an uuid of file to process
- **audio_model**: an audio processing model name (check '_/audio/models_' for available models)
- **image_file**: an uuid of file to process
- **image_model**: an image processing model name (check '_/image/models_' for available models)

Responses:
- 200, Task created
- 404, No such audio file available
- 404, No such audio model available
- 404, No such image file available
- 404, No such image model available

> Body parameter

```json
{
  "audio_file": "732b10bd-0006-4780-8f48-4319d2791290",
  "image_file": "89f23c23-fe12-4935-b746-3bbc447c7a72",
  "audio_model": "string",
  "image_model": "string"
}
```

<h3 id="the-endpoint-`/audio/image/task`-creates-a-task-to-compare-an-audio-against-image-file-using-specified
----models-and-returns-the-task-id.-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|[AudioToImageComparisonRequest](#schemaaudiotoimagecomparisonrequest)|true|none|
|» audio_file|body|string(uuid)|true|none|
|» image_file|body|string(uuid)|true|none|
|» audio_model|body|string|true|none|
|» image_model|body|string|true|none|

> Example responses

> 200 Response

```json
{
  "task_id": "736fde4d-9029-4915-8189-01353d6982cb"
}
```

> 404 Response

```json
{
  "detail": "No such image model available"
}
```

<h3 id="the-endpoint-`/audio/image/task`-creates-a-task-to-compare-an-audio-against-image-file-using-specified
----models-and-returns-the-task-id.-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Task was successfully created and scheduled|[TaskCreateResponse](#schemataskcreateresponse)|
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|The specified file or model was not found.|None|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|

<h3 id="the-endpoint-`/audio/image/task`-creates-a-task-to-compare-an-audio-against-image-file-using-specified
----models-and-returns-the-task-id.-responseschema">Response Schema</h3>

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2PasswordBearer
</aside>

## The endpoint `/audio/image/result` retrieves the results of a task with a given task ID, and returns the
    results.

<a id="opIdget_audio_image_comparison_result_v1_comparison_audio_image_result_get"></a>

> Code samples

`GET /v1/comparison/audio/image/result`

Parameters:
- **task_id**: The `task_id` is the uuid of the task to fetch results of

Responses:
- 200, job results in the format
```js
{
"image": { // image proccessing result
    "text": "string", // total extracted text
    "boxes": [ // list of boxes with text
    {
        "text": "string", // text extracted from the box
        "coordinates": { // coordinates of the box on the image
        "left_top": { // four points defining a rectangle
            "x": 0,
            "y": 0
        },
        "right_top": {
            "x": 0,
            "y": 0
        },
        "left_bottom": {
            "x": 0,
            "y": 0
        },
        "right_bottom": {
            "x": 0,
            "y": 0
        }
        }
    }
    ]
},
"audio": { // audio processing results
    "text": "string", // total extracted text
    "segments": [ // audio segments, that were processed
    {
        "start": 0, // absolute time code of the beginning of the segment
        "end": 0, // absolute time code of the ending of the segment
        "text": "string", // text extracted from the segment
        "file": "3fa85f64-5717-4562-b3fc-2c963f66afa6" // audio segment
    }
    ]
},
"errors": [ // results of comparing
    {
    "audio_segment": { // audio segment where error was made
        "start": 0,
        "end": 0,
        "text": "string",
        "file": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
    },
    "at_char": 0, // chat, at which an error stats
    "found": "string", // found word (based on audio)
    "expected": "string" // exptected word (suggetion for improvement based on image)
    }
]
}
```
- 406, Results are not ready yet or no task with such id exist
- 422, There is no such audio processing task

<h3 id="the-endpoint-`/audio/image/result`-retrieves-the-results-of-a-task-with-a-given-task-id,-and-returns-the
----results.-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|task_id|query|string(uuid)|true|none|

> Example responses

> 200 Response

```json
{
  "image": {
    "text": "string",
    "boxes": [
      {
        "text": "string",
        "coordinates": {
          "left_top": {
            "x": 0,
            "y": 0
          },
          "right_top": {
            "x": 0,
            "y": 0
          },
          "left_bottom": {
            "x": 0,
            "y": 0
          },
          "right_bottom": {
            "x": 0,
            "y": 0
          }
        }
      }
    ]
  },
  "audio": {
    "text": "string",
    "segments": [
      {
        "start": 0,
        "end": 0,
        "text": "string",
        "file": "00bd29cf-1ab3-4825-b15f-d80a4a0e1cbb"
      }
    ]
  },
  "errors": [
    {
      "audio_segment": {
        "start": 0,
        "end": 0,
        "text": "string",
        "file": "00bd29cf-1ab3-4825-b15f-d80a4a0e1cbb"
      },
      "at_char": 0,
      "found": "string",
      "expected": "string"
    }
  ]
}
```

> 406 Response

```json
{
  "detail": "Results are not ready yet or no task with such id exist"
}
```

> 422 Response

```json
{
  "detail": "There is no such task consists of the both image and audio"
}
```

<h3 id="the-endpoint-`/audio/image/result`-retrieves-the-results-of-a-task-with-a-given-task-id,-and-returns-the
----results.-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|[AudioImageComparisonResultsResponse](#schemaaudioimagecomparisonresultsresponse)|
|406|[Not Acceptable](https://tools.ietf.org/html/rfc7231#section-6.5.6)|It is impossible to get task result (task does not exist or it has not finished yet).|None|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|There is no such task consists of the both image and audio.|None|

<h3 id="the-endpoint-`/audio/image/result`-retrieves-the-results-of-a-task-with-a-given-task-id,-and-returns-the
----results.-responseschema">Response Schema</h3>

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2PasswordBearer
</aside>

## The endpoint '/audio/text/task' creates a task to compare audio against text from user input 
    using specified models and returns the task ID.

<a id="opIdcompare_audio_to_text_v1_comparison_audio_text_task_post"></a>

> Code samples

`POST /v1/comparison/audio/text/task`

Parameters:
- **audio_file**: an uuid of file to process
- **audio_model**: an audio processing model name (check '_/audio/models_' for available models)
- **text**: a list of strings to compare audio against

Responses:
- 200, Task created
- 404, No such audio file available
- 404, No such audio model available

> Body parameter

```json
{
  "audio_file": "732b10bd-0006-4780-8f48-4319d2791290",
  "text": [
    "string"
  ],
  "audio_model": "string"
}
```

<h3 id="the-endpoint-'/audio/text/task'-creates-a-task-to-compare-audio-against-text-from-user-input-
----using-specified-models-and-returns-the-task-id.-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|[AudioToTextComparisonRequest](#schemaaudiototextcomparisonrequest)|true|none|
|» audio_file|body|string(uuid)|true|none|
|» text|body|[string]|true|none|
|» audio_model|body|string|true|none|

> Example responses

> 200 Response

```json
{
  "task_id": "736fde4d-9029-4915-8189-01353d6982cb"
}
```

> 404 Response

```json
{
  "detail": "No such audio model available"
}
```

<h3 id="the-endpoint-'/audio/text/task'-creates-a-task-to-compare-audio-against-text-from-user-input-
----using-specified-models-and-returns-the-task-id.-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Task was successfully created and scheduled|[TaskCreateResponse](#schemataskcreateresponse)|
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|The specified file or model was not found.|None|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|

<h3 id="the-endpoint-'/audio/text/task'-creates-a-task-to-compare-audio-against-text-from-user-input-
----using-specified-models-and-returns-the-task-id.-responseschema">Response Schema</h3>

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2PasswordBearer
</aside>

## The endpoint `/audio/text/result` retrieves the results of a task with a given task ID, and returns the
    results.

<a id="opIdget_audio_text_comparison_result_v1_comparison_audio_text_result_get"></a>

> Code samples

`GET /v1/comparison/audio/text/result`

Parameters:
- **task_id**: The `task_id` is the uuid of the task to fetch results of

Responses:
- 200, job results in the format
```js
{
"audio": { // audio processing results
    "text": "string", // total extracted text
    "segments": [ // audio segments, that were processed
    {
        "start": 0, // absolute time code of the beginning of the segment
        "end": 0, // absolute time code of the ending of the segment
        "text": "string", // text extracted from the segment
        "file": "3fa85f64-5717-4562-b3fc-2c963f66afa6" // audio segment
    }
    ]
},
"errors": [ // results of comparing
    {
    "audio_segment": { // audio segment where error was made
        "start": 0,
        "end": 0,
        "text": "string",
        "file": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
    },
    "at_char": 0, // chat, at which an error stats
    "found": "string", // found word (based on audio)
    "expected": "string" // exptected word (suggetion for improvement based on text)
    }
]
}
```
- 406, Results are not ready yet or no task with such id exist
- 422, There is no such audio processing task

<h3 id="the-endpoint-`/audio/text/result`-retrieves-the-results-of-a-task-with-a-given-task-id,-and-returns-the
----results.-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|task_id|query|string(uuid)|true|none|

> Example responses

> 200 Response

```json
{
  "audio": {
    "text": "string",
    "segments": [
      {
        "start": 0,
        "end": 0,
        "text": "string",
        "file": "00bd29cf-1ab3-4825-b15f-d80a4a0e1cbb"
      }
    ]
  },
  "errors": [
    {
      "audio_segment": {
        "start": 0,
        "end": 0,
        "text": "string",
        "file": "00bd29cf-1ab3-4825-b15f-d80a4a0e1cbb"
      },
      "at_char": 0,
      "found": "string",
      "expected": "string"
    }
  ]
}
```

> 406 Response

```json
{
  "detail": "Results are not ready yet or no task with such id exist"
}
```

> 422 Response

```json
{
  "detail": "There is no such task consists of the both audio and text"
}
```

<h3 id="the-endpoint-`/audio/text/result`-retrieves-the-results-of-a-task-with-a-given-task-id,-and-returns-the
----results.-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|[AudioTextComparisonResultsResponse](#schemaaudiotextcomparisonresultsresponse)|
|406|[Not Acceptable](https://tools.ietf.org/html/rfc7231#section-6.5.6)|It is impossible to get task result (task does not exist or it has not finished yet).|None|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|There is no such task consists of the both audio and text.|None|

<h3 id="the-endpoint-`/audio/text/result`-retrieves-the-results-of-a-task-with-a-given-task-id,-and-returns-the
----results.-responseschema">Response Schema</h3>

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2PasswordBearer
</aside>

<h1 id="fastapi-task">task</h1>

## The endpoint `status` returns the status of a task identified by its `task_id`.

<a id="opIdget_job_status_v1_task_status_get"></a>

> Code samples

`GET /v1/task/status`

Parameters:
- **task_id**: The `task_id` is the uuid of the task to fetch status of

Responses:
- 200, Job status

<h3 id="the-endpoint-`status`-returns-the-status-of-a-task-identified-by-its-`task_id`.-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|task_id|query|string(uuid)|true|none|

> Example responses

> 200 Response

```json
{
  "task_id": "736fde4d-9029-4915-8189-01353d6982cb",
  "status": "string",
  "ready": true
}
```

<h3 id="the-endpoint-`status`-returns-the-status-of-a-task-identified-by-its-`task_id`.-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|[TaskStatusResponse](#schemataskstatusresponse)|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2PasswordBearer
</aside>

## The endpoint `/result` retrieves the results of a task with a given task ID, and returns the
    results.

<a id="opIdget_job_result_v1_task_result_get"></a>

> Code samples

`GET /v1/task/result`

Parameters:
- **task_id**: The `task_id` is the uuid of the task to fetch results of

Responses:
- 200, job results
- 406, Results are not ready yet or no task with such id exist

<h3 id="the-endpoint-`/result`-retrieves-the-results-of-a-task-with-a-given-task-id,-and-returns-the
----results.-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|task_id|query|string(uuid)|true|none|

> Example responses

> 200 Response

```json
{}
```

> 406 Response

```json
{
  "detail": "Results are not ready yet or no task with such id exist"
}
```

<h3 id="the-endpoint-`/result`-retrieves-the-results-of-a-task-with-a-given-task-id,-and-returns-the
----results.-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|Inline|
|406|[Not Acceptable](https://tools.ietf.org/html/rfc7231#section-6.5.6)|It is impossible to get task result (task does not exist or it has not finished yet).|None|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|

<h3 id="the-endpoint-`/result`-retrieves-the-results-of-a-task-with-a-given-task-id,-and-returns-the
----results.-responseschema">Response Schema</h3>

Status Code **200**

*Response Get Job Result V1 Task Result Get*

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2PasswordBearer
</aside>

# Schemas

<h2 id="tocS_AudioChunk">AudioChunk</h2>
<!-- backwards compatibility -->
<a id="schemaaudiochunk"></a>
<a id="schema_AudioChunk"></a>
<a id="tocSaudiochunk"></a>
<a id="tocsaudiochunk"></a>

```json
{
  "start": 0,
  "end": 0,
  "text": "string",
  "file": "00bd29cf-1ab3-4825-b15f-d80a4a0e1cbb"
}

```

AudioChunk

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|start|number|true|none|none|
|end|number|true|none|none|
|text|string|true|none|none|
|file|string(uuid)|true|none|none|

<h2 id="tocS_AudioExtractPhrasesRequest">AudioExtractPhrasesRequest</h2>
<!-- backwards compatibility -->
<a id="schemaaudioextractphrasesrequest"></a>
<a id="schema_AudioExtractPhrasesRequest"></a>
<a id="tocSaudioextractphrasesrequest"></a>
<a id="tocsaudioextractphrasesrequest"></a>

```json
{
  "audio_file": "732b10bd-0006-4780-8f48-4319d2791290",
  "audio_model": "string",
  "phrases": [
    "string"
  ]
}

```

AudioExtractPhrasesRequest

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|audio_file|string(uuid)|true|none|none|
|audio_model|string|true|none|none|
|phrases|[string]|true|none|none|

<h2 id="tocS_AudioExtractPhrasesResponse">AudioExtractPhrasesResponse</h2>
<!-- backwards compatibility -->
<a id="schemaaudioextractphrasesresponse"></a>
<a id="schema_AudioExtractPhrasesResponse"></a>
<a id="tocSaudioextractphrasesresponse"></a>
<a id="tocsaudioextractphrasesresponse"></a>

```json
{
  "data": [
    {
      "audio_segment": {
        "start": 0,
        "end": 0,
        "text": "string",
        "file": "00bd29cf-1ab3-4825-b15f-d80a4a0e1cbb"
      },
      "found": true,
      "phrase": "string"
    }
  ]
}

```

AudioExtractPhrasesResponse

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|data|[[AudioPhrase](#schemaaudiophrase)]|true|none|none|

<h2 id="tocS_AudioImageComparisonResultsResponse">AudioImageComparisonResultsResponse</h2>
<!-- backwards compatibility -->
<a id="schemaaudioimagecomparisonresultsresponse"></a>
<a id="schema_AudioImageComparisonResultsResponse"></a>
<a id="tocSaudioimagecomparisonresultsresponse"></a>
<a id="tocsaudioimagecomparisonresultsresponse"></a>

```json
{
  "image": {
    "text": "string",
    "boxes": [
      {
        "text": "string",
        "coordinates": {
          "left_top": {
            "x": 0,
            "y": 0
          },
          "right_top": {
            "x": 0,
            "y": 0
          },
          "left_bottom": {
            "x": 0,
            "y": 0
          },
          "right_bottom": {
            "x": 0,
            "y": 0
          }
        }
      }
    ]
  },
  "audio": {
    "text": "string",
    "segments": [
      {
        "start": 0,
        "end": 0,
        "text": "string",
        "file": "00bd29cf-1ab3-4825-b15f-d80a4a0e1cbb"
      }
    ]
  },
  "errors": [
    {
      "audio_segment": {
        "start": 0,
        "end": 0,
        "text": "string",
        "file": "00bd29cf-1ab3-4825-b15f-d80a4a0e1cbb"
      },
      "at_char": 0,
      "found": "string",
      "expected": "string"
    }
  ]
}

```

AudioImageComparisonResultsResponse

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|image|[ImageProcessingResponse](#schemaimageprocessingresponse)|true|none|none|
|audio|[AudioProcessingResponse](#schemaaudioprocessingresponse)|true|none|none|
|errors|[[TextDiff](#schematextdiff)]|true|none|none|

<h2 id="tocS_AudioPhrase">AudioPhrase</h2>
<!-- backwards compatibility -->
<a id="schemaaudiophrase"></a>
<a id="schema_AudioPhrase"></a>
<a id="tocSaudiophrase"></a>
<a id="tocsaudiophrase"></a>

```json
{
  "audio_segment": {
    "start": 0,
    "end": 0,
    "text": "string",
    "file": "00bd29cf-1ab3-4825-b15f-d80a4a0e1cbb"
  },
  "found": true,
  "phrase": "string"
}

```

AudioPhrase

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|audio_segment|[AudioChunk](#schemaaudiochunk)|false|none|none|
|found|boolean|true|none|none|
|phrase|string|true|none|none|

<h2 id="tocS_AudioProcessingRequest">AudioProcessingRequest</h2>
<!-- backwards compatibility -->
<a id="schemaaudioprocessingrequest"></a>
<a id="schema_AudioProcessingRequest"></a>
<a id="tocSaudioprocessingrequest"></a>
<a id="tocsaudioprocessingrequest"></a>

```json
{
  "audio_file": "732b10bd-0006-4780-8f48-4319d2791290",
  "audio_model": "string"
}

```

AudioProcessingRequest

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|audio_file|string(uuid)|true|none|none|
|audio_model|string|true|none|none|

<h2 id="tocS_AudioProcessingResponse">AudioProcessingResponse</h2>
<!-- backwards compatibility -->
<a id="schemaaudioprocessingresponse"></a>
<a id="schema_AudioProcessingResponse"></a>
<a id="tocSaudioprocessingresponse"></a>
<a id="tocsaudioprocessingresponse"></a>

```json
{
  "text": "string",
  "segments": [
    {
      "start": 0,
      "end": 0,
      "text": "string",
      "file": "00bd29cf-1ab3-4825-b15f-d80a4a0e1cbb"
    }
  ]
}

```

AudioProcessingResponse

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|text|string|true|none|none|
|segments|[[AudioChunk](#schemaaudiochunk)]|true|none|none|

<h2 id="tocS_AudioTextComparisonResultsResponse">AudioTextComparisonResultsResponse</h2>
<!-- backwards compatibility -->
<a id="schemaaudiotextcomparisonresultsresponse"></a>
<a id="schema_AudioTextComparisonResultsResponse"></a>
<a id="tocSaudiotextcomparisonresultsresponse"></a>
<a id="tocsaudiotextcomparisonresultsresponse"></a>

```json
{
  "audio": {
    "text": "string",
    "segments": [
      {
        "start": 0,
        "end": 0,
        "text": "string",
        "file": "00bd29cf-1ab3-4825-b15f-d80a4a0e1cbb"
      }
    ]
  },
  "errors": [
    {
      "audio_segment": {
        "start": 0,
        "end": 0,
        "text": "string",
        "file": "00bd29cf-1ab3-4825-b15f-d80a4a0e1cbb"
      },
      "at_char": 0,
      "found": "string",
      "expected": "string"
    }
  ]
}

```

AudioTextComparisonResultsResponse

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|audio|[AudioProcessingResponse](#schemaaudioprocessingresponse)|true|none|none|
|errors|[[TextDiff](#schematextdiff)]|true|none|none|

<h2 id="tocS_AudioToImageComparisonRequest">AudioToImageComparisonRequest</h2>
<!-- backwards compatibility -->
<a id="schemaaudiotoimagecomparisonrequest"></a>
<a id="schema_AudioToImageComparisonRequest"></a>
<a id="tocSaudiotoimagecomparisonrequest"></a>
<a id="tocsaudiotoimagecomparisonrequest"></a>

```json
{
  "audio_file": "732b10bd-0006-4780-8f48-4319d2791290",
  "image_file": "89f23c23-fe12-4935-b746-3bbc447c7a72",
  "audio_model": "string",
  "image_model": "string"
}

```

AudioToImageComparisonRequest

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|audio_file|string(uuid)|true|none|none|
|image_file|string(uuid)|true|none|none|
|audio_model|string|true|none|none|
|image_model|string|true|none|none|

<h2 id="tocS_AudioToTextComparisonRequest">AudioToTextComparisonRequest</h2>
<!-- backwards compatibility -->
<a id="schemaaudiototextcomparisonrequest"></a>
<a id="schema_AudioToTextComparisonRequest"></a>
<a id="tocSaudiototextcomparisonrequest"></a>
<a id="tocsaudiototextcomparisonrequest"></a>

```json
{
  "audio_file": "732b10bd-0006-4780-8f48-4319d2791290",
  "text": [
    "string"
  ],
  "audio_model": "string"
}

```

AudioToTextComparisonRequest

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|audio_file|string(uuid)|true|none|none|
|text|[string]|true|none|none|
|audio_model|string|true|none|none|

<h2 id="tocS_Body_login_for_access_token_v1_auth_token_post">Body_login_for_access_token_v1_auth_token_post</h2>
<!-- backwards compatibility -->
<a id="schemabody_login_for_access_token_v1_auth_token_post"></a>
<a id="schema_Body_login_for_access_token_v1_auth_token_post"></a>
<a id="tocSbody_login_for_access_token_v1_auth_token_post"></a>
<a id="tocsbody_login_for_access_token_v1_auth_token_post"></a>

```json
{
  "grant_type": "string",
  "username": "string",
  "password": "string",
  "scope": "",
  "client_id": "string",
  "client_secret": "string"
}

```

Body_login_for_access_token_v1_auth_token_post

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|grant_type|string|false|none|none|
|username|string|true|none|none|
|password|string|true|none|none|
|scope|string|false|none|none|
|client_id|string|false|none|none|
|client_secret|string|false|none|none|

<h2 id="tocS_Body_upload_audio_file_v1_audio_upload_post">Body_upload_audio_file_v1_audio_upload_post</h2>
<!-- backwards compatibility -->
<a id="schemabody_upload_audio_file_v1_audio_upload_post"></a>
<a id="schema_Body_upload_audio_file_v1_audio_upload_post"></a>
<a id="tocSbody_upload_audio_file_v1_audio_upload_post"></a>
<a id="tocsbody_upload_audio_file_v1_audio_upload_post"></a>

```json
{
  "upload_file": "string"
}

```

Body_upload_audio_file_v1_audio_upload_post

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|upload_file|string(binary)|true|none|none|

<h2 id="tocS_Body_upload_image_v1_image_upload_post">Body_upload_image_v1_image_upload_post</h2>
<!-- backwards compatibility -->
<a id="schemabody_upload_image_v1_image_upload_post"></a>
<a id="schema_Body_upload_image_v1_image_upload_post"></a>
<a id="tocSbody_upload_image_v1_image_upload_post"></a>
<a id="tocsbody_upload_image_v1_image_upload_post"></a>

```json
{
  "upload_file": "string"
}

```

Body_upload_image_v1_image_upload_post

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|upload_file|string(binary)|true|none|none|

<h2 id="tocS_HTTPValidationError">HTTPValidationError</h2>
<!-- backwards compatibility -->
<a id="schemahttpvalidationerror"></a>
<a id="schema_HTTPValidationError"></a>
<a id="tocShttpvalidationerror"></a>
<a id="tocshttpvalidationerror"></a>

```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string"
    }
  ]
}

```

HTTPValidationError

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|detail|[[ValidationError](#schemavalidationerror)]|false|none|none|

<h2 id="tocS_IPRPoint">IPRPoint</h2>
<!-- backwards compatibility -->
<a id="schemaiprpoint"></a>
<a id="schema_IPRPoint"></a>
<a id="tocSiprpoint"></a>
<a id="tocsiprpoint"></a>

```json
{
  "x": 0,
  "y": 0
}

```

IPRPoint

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|x|integer|true|none|none|
|y|integer|true|none|none|

<h2 id="tocS_IPRRectangle">IPRRectangle</h2>
<!-- backwards compatibility -->
<a id="schemaiprrectangle"></a>
<a id="schema_IPRRectangle"></a>
<a id="tocSiprrectangle"></a>
<a id="tocsiprrectangle"></a>

```json
{
  "left_top": {
    "x": 0,
    "y": 0
  },
  "right_top": {
    "x": 0,
    "y": 0
  },
  "left_bottom": {
    "x": 0,
    "y": 0
  },
  "right_bottom": {
    "x": 0,
    "y": 0
  }
}

```

IPRRectangle

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|left_top|[IPRPoint](#schemaiprpoint)|true|none|none|
|right_top|[IPRPoint](#schemaiprpoint)|true|none|none|
|left_bottom|[IPRPoint](#schemaiprpoint)|true|none|none|
|right_bottom|[IPRPoint](#schemaiprpoint)|true|none|none|

<h2 id="tocS_IPRTextBox">IPRTextBox</h2>
<!-- backwards compatibility -->
<a id="schemaiprtextbox"></a>
<a id="schema_IPRTextBox"></a>
<a id="tocSiprtextbox"></a>
<a id="tocsiprtextbox"></a>

```json
{
  "text": "string",
  "coordinates": {
    "left_top": {
      "x": 0,
      "y": 0
    },
    "right_top": {
      "x": 0,
      "y": 0
    },
    "left_bottom": {
      "x": 0,
      "y": 0
    },
    "right_bottom": {
      "x": 0,
      "y": 0
    }
  }
}

```

IPRTextBox

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|text|string|true|none|none|
|coordinates|[IPRRectangle](#schemaiprrectangle)|true|none|none|

<h2 id="tocS_ImageProcessingRequest">ImageProcessingRequest</h2>
<!-- backwards compatibility -->
<a id="schemaimageprocessingrequest"></a>
<a id="schema_ImageProcessingRequest"></a>
<a id="tocSimageprocessingrequest"></a>
<a id="tocsimageprocessingrequest"></a>

```json
{
  "image_file": "89f23c23-fe12-4935-b746-3bbc447c7a72",
  "image_model": "string"
}

```

ImageProcessingRequest

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|image_file|string(uuid)|true|none|none|
|image_model|string|true|none|none|

<h2 id="tocS_ImageProcessingResponse">ImageProcessingResponse</h2>
<!-- backwards compatibility -->
<a id="schemaimageprocessingresponse"></a>
<a id="schema_ImageProcessingResponse"></a>
<a id="tocSimageprocessingresponse"></a>
<a id="tocsimageprocessingresponse"></a>

```json
{
  "text": "string",
  "boxes": [
    {
      "text": "string",
      "coordinates": {
        "left_top": {
          "x": 0,
          "y": 0
        },
        "right_top": {
          "x": 0,
          "y": 0
        },
        "left_bottom": {
          "x": 0,
          "y": 0
        },
        "right_bottom": {
          "x": 0,
          "y": 0
        }
      }
    }
  ]
}

```

ImageProcessingResponse

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|text|string|true|none|none|
|boxes|[[IPRTextBox](#schemaiprtextbox)]|true|none|none|

<h2 id="tocS_ModelData">ModelData</h2>
<!-- backwards compatibility -->
<a id="schemamodeldata"></a>
<a id="schema_ModelData"></a>
<a id="tocSmodeldata"></a>
<a id="tocsmodeldata"></a>

```json
{
  "name": "string",
  "languages": [
    "string"
  ],
  "description": "string"
}

```

ModelData

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|name|string|true|none|none|
|languages|[string]|true|none|none|
|description|string|true|none|none|

<h2 id="tocS_ModelsDataReponse">ModelsDataReponse</h2>
<!-- backwards compatibility -->
<a id="schemamodelsdatareponse"></a>
<a id="schema_ModelsDataReponse"></a>
<a id="tocSmodelsdatareponse"></a>
<a id="tocsmodelsdatareponse"></a>

```json
{
  "models": [
    {
      "name": "string",
      "languages": [
        "string"
      ],
      "description": "string"
    }
  ]
}

```

ModelsDataReponse

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|models|[[ModelData](#schemamodeldata)]|true|none|none|

<h2 id="tocS_RegisterResponse">RegisterResponse</h2>
<!-- backwards compatibility -->
<a id="schemaregisterresponse"></a>
<a id="schema_RegisterResponse"></a>
<a id="tocSregisterresponse"></a>
<a id="tocsregisterresponse"></a>

```json
{
  "text": "string"
}

```

RegisterResponse

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|text|string|true|none|none|

<h2 id="tocS_TaskCreateResponse">TaskCreateResponse</h2>
<!-- backwards compatibility -->
<a id="schemataskcreateresponse"></a>
<a id="schema_TaskCreateResponse"></a>
<a id="tocStaskcreateresponse"></a>
<a id="tocstaskcreateresponse"></a>

```json
{
  "task_id": "736fde4d-9029-4915-8189-01353d6982cb"
}

```

TaskCreateResponse

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|task_id|string(uuid)|true|none|none|

<h2 id="tocS_TaskStatusResponse">TaskStatusResponse</h2>
<!-- backwards compatibility -->
<a id="schemataskstatusresponse"></a>
<a id="schema_TaskStatusResponse"></a>
<a id="tocStaskstatusresponse"></a>
<a id="tocstaskstatusresponse"></a>

```json
{
  "task_id": "736fde4d-9029-4915-8189-01353d6982cb",
  "status": "string",
  "ready": true
}

```

TaskStatusResponse

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|task_id|string(uuid)|true|none|none|
|status|string|true|none|none|
|ready|boolean|true|none|none|

<h2 id="tocS_TextDiff">TextDiff</h2>
<!-- backwards compatibility -->
<a id="schematextdiff"></a>
<a id="schema_TextDiff"></a>
<a id="tocStextdiff"></a>
<a id="tocstextdiff"></a>

```json
{
  "audio_segment": {
    "start": 0,
    "end": 0,
    "text": "string",
    "file": "00bd29cf-1ab3-4825-b15f-d80a4a0e1cbb"
  },
  "at_char": 0,
  "found": "string",
  "expected": "string"
}

```

TextDiff

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|audio_segment|[AudioChunk](#schemaaudiochunk)|true|none|none|
|at_char|integer|true|none|none|
|found|string|true|none|none|
|expected|string|true|none|none|

<h2 id="tocS_Token">Token</h2>
<!-- backwards compatibility -->
<a id="schematoken"></a>
<a id="schema_Token"></a>
<a id="tocStoken"></a>
<a id="tocstoken"></a>

```json
{
  "access_token": "string",
  "token_type": "string"
}

```

Token

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|access_token|string|true|none|none|
|token_type|string|true|none|none|

<h2 id="tocS_UploadFileResponse">UploadFileResponse</h2>
<!-- backwards compatibility -->
<a id="schemauploadfileresponse"></a>
<a id="schema_UploadFileResponse"></a>
<a id="tocSuploadfileresponse"></a>
<a id="tocsuploadfileresponse"></a>

```json
{
  "file_id": "8a0cfb4f-ddc9-436d-91bb-75133c583767"
}

```

UploadFileResponse

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|file_id|string(uuid)|true|none|none|

<h2 id="tocS_User">User</h2>
<!-- backwards compatibility -->
<a id="schemauser"></a>
<a id="schema_User"></a>
<a id="tocSuser"></a>
<a id="tocsuser"></a>

```json
{
  "username": "string",
  "email": "string",
  "full_name": "string",
  "disabled": true
}

```

User

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|username|string|true|none|none|
|email|string|false|none|none|
|full_name|string|false|none|none|
|disabled|boolean|false|none|none|

<h2 id="tocS_ValidationError">ValidationError</h2>
<!-- backwards compatibility -->
<a id="schemavalidationerror"></a>
<a id="schema_ValidationError"></a>
<a id="tocSvalidationerror"></a>
<a id="tocsvalidationerror"></a>

```json
{
  "loc": [
    "string"
  ],
  "msg": "string",
  "type": "string"
}

```

ValidationError

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|loc|[anyOf]|true|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|msg|string|true|none|none|
|type|string|true|none|none|

<script type="application/ld+json">
{
  "@context": "http://schema.org/",
  "@type": "WebAPI",
  
  
  
  
  "name": "FastAPI"
}
</script>

# Advanced
# Audio
## Audio Conversion
Our system uses the [pydub python package](https://github.com/jiaaro/pydub#pydub) 
 to work with audio files. The `pydub` package is a high-level audio library that simplifies the process of audio file manipulation. This package relies on [FFmpeg framework](https://www.ffmpeg.org/about.html). FFmpeg is a multimedia framework that enables the operation of various audio and video file formats.

The `pydub` package and `FFmpeg` framework, together, support various audio file formats, including MP3, WAV, FLAC, M4A, among others. However, it is important to note that uploading of audio files to our system is restricted to the most general audio formats specified by MIMO. This is to ensure convenience and prevent errors when processing the uploaded files.

List of the most important allowed extensions:
- .acc
- .mp3
- .m4a
- .oga, .ogv
- .ogg
- .opus
- .wav 

For a comprehensive list of the supported formats, please refer to:
[Full list of FFmpeg supported formats](http://www.ffmpeg.org/general.html#File-Formats)

## Audio Models
Our system fetches audio models from a worker that loads plugins. This process is carried out by sending a request to the worker, which then returns the loaded plugins. The worker is responsible for loading audio processing plugins, which include machine learning models for audio analysis and other related functionalities.

To initiate this process, our system sends a request to the worker to retrieve the list of loaded plugins that are ready to use. This helps ensure that the audio models used in the system are up-to-date.

# Image
## Image
## Image Models
Our system fetches image models from a worker that loads plugins. This process is carried out by sending a request to the worker, which then returns the loaded plugins. The worker is responsible for loading image processing plugins, which include machine learning models for image analysis and other related functionalities.

To initiate this process, our system sends a request to the worker to retrieve the list of loaded plugins that are ready to use. This helps ensure that the image models used in the system are up-to-date.

# Task System
This is a set of functions and methods used in Follow My Reading task system.

## `_plugin_class_method_call`
`_plugin_class_method_call()` is a helper function that searches each plugin for class_name object. If the object is found, it loads the function from it and calls it with the filepath argument. It returns the result of the function.

## `dynamic_plugin_call`
`dynamic_plugin_call()` is a scheduled job that accepts class_name, function, and filepath as parameters. It calls _plugin_class_method_call() with these parameters.

## `load_plugins_into_memories`
`load_plugins_into_memories()` is a startup function that loads plugins.

## `audio_processing_call`
`audio_processing_call()` is a scheduled job that accepts audio_class, audio_function, and audio_path as parameters. It calls _audio_process() with these parameters.

## `image_processing_call`
`image_processing_call()` is a scheduled job that accepts image_class, image_function, and image_path as parameters. It calls _image_process() with these parameters.

## `compare_audio_image`
`compare_audio_image()` is a scheduled job that accepts audio_class, audio_function, audio_path, image_class, image_function, and image_path as parameters. It calls _audio_process() and _image_process() with these parameters. It matches resulted texts and returns the difference.

## `compare_audio_text`
`compare_audio_text()` is a scheduled job that accepts audio_class, audio_function, audio_path, and text as parameters. It calls _audio_process() with these parameters. It matches resulted texts and returns the difference.

## `_get_audio_plugins`
`_get_audio_plugins()` is a scheduled job that returns information about loaded audio plugins.

## `_get_image_plugins`
`_get_image_plugins()` is a scheduled job that returns information about loaded image plugins.

## `_extact_phrases_from_audio`
`_extact_phrases_from_audio()` is a helper function that extracts text from audio and searches for each phrase. It splits the audio by non-none intervals and assigns the splitted files. It returns the result of audio phrases extraction.

## `extact_phrases_from_audio`
`extact_phrases_from_audio()` is a scheduled job that accepts audio_class, audio_path, and phrases as parameters

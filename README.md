# Follow My Reading

### Project start
```
redis-server & rq worker --with-scheduler & uvicorn main:app
```

### Type Validation:
```
mypy --ignore-missing-imports  --follow-imports=skip --strict .
```


API Design
```
GET /v1/docs
    description: Returns a list of methods
    body: -
    headers: -
    query: -
    responses:
        200:
            *openapi format documentation*

GET /v1/image/models
    description: Returns a list of models available for image processing
    body: -
    headers: -
    query: -
    responses:
        200:
            {
                models: [
                    {
                        id: int
                        name: string
                        description: string
                    }
                ]
            }
GET /v1/audio/models
    description: Returns a list of models available for audio processing
    body: -
    headers: -
    query: -
    responses:
        200:
            {
                models: [
                    {
                        id: int
                        name: string
                        description: string
                    }
                ]
            }


POST /v1/image/upload
    description: Upload file to the server and get uuid
    body:
        image: File (byte data)
    headers: -
    query: 0
    responses:
        200:
            {
                uuid: uuidv4
            }
        409:
            {
                description: "Wrong data type"
            }
        403:
            {
                description: "Too large file"
            }

POST /v1/audio/upload
    description: Uploads audio to the server and gets uuid
    body:
        image: File (byte data)
    headers: -
    query: 0
    responses:
        200:
            {
                uuid: uuidv4
            }
        409:
            {
                description: string
            }
        403:
            {
                description: string
            }

POST /v1/task/create
    description: Creates a new task for processing image and audio
    body:
        {
            audio: uuid
            image: uuid
            audio_model: uuid
            image_model: uuid
        }
    headers: -
    query: -
    reposnses:
        201:
            {
                task_uuid: uuid
            }
        409:
            {
                description: string
            }

GET /v1/task/status?uuid={uuid}
    description: Fetches status of the task
    body: -
    query:
        uuid: uuid
    headers: -
    responses:
        404:
            {
                description: string
            }
        200:
            {
                status: string
                ready: bool
            }
GET /v1/task/results?uuid={uuid}
    description: Fetches results of the task
    body: -
    query:
        uuid: uuid
    headers: -
    responses:
        404:
            {
                description: string
            }
        403:
            {
                description: string
            }
        200:
            {
                spend_time: int
                status: string
                result: [
                    {
                        index: int
                        text: string
                        audio: File
                        coordintates: {
                            x: int
                            y: int
                        }
                    }
                ]
            }

DELETE /v1/task/terminate?uuid={uuid}
    description: Kill task
    body: -
    headers: -
    query:
        uuid: uuid
    reposenses:
        404:
            {
                description: string
            }
        409:
            {
                description: string
            }
        200:
            {
                status: string
            }
```
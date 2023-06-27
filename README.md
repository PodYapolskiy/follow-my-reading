# Follow My Reading

## Set up
To set up the project run the following command in the terminal
```bash
pip install poetry
poetry install
```

## Launch
Run redis server
```bash
redis-server
```

Run huey consumer
```bash
huey_consumer.py core.task_system.scheduler -n -k thread
```

Run server
```
uvicorn main:app
```

## Models

### EasyOCR
More: https://github.com/JaidedAI/EasyOCR
```
easyocr -l en -f image.jpg --detail=1 --gpu=False
```

### VOSK
```bash
vosk-transcriber -i audio.mp4 -o text.txt
```

### PaddleOCR
More: https://github.com/PaddlePaddle/PaddleOCR/blob/release/2.6/doc/doc_en/quickstart_en.md#21-use-by-command-line
```bash
paddleocr --image_dir image.jpg --use_angle_cls true --lang=ru --use_gpu false
```



FROM python:3.10
# update system
RUN apt update --no-install-recommends -y
RUN apt upgrade -y
RUN apt-get update -y
# install dependencies
RUN apt-get install libsndfile-dev ffmpeg cuda-toolkit-* -y
# install redis server
RUN apt install redis-server -y
# install tesseract
RUN apt install tesseract-ocr -y
# download trained data for tesseract
ENV TESSDATA_PREFIX /tessdata
RUN mkdir ${TESSDATA_PREFIX}
# english
RUN curl -o ${TESSDATA_PREFIX}/eng.traineddata \
    -H 'Accept: application/vnd.github.v3.raw' \
    -L https://github.com/tesseract-ocr/tessdata_best/raw/main/eng.traineddata
# russian
RUN curl -o ${TESSDATA_PREFIX}/rus.traineddata \
    -H 'Accept: application/vnd.github.v3.raw' \
    -L https://github.com/tesseract-ocr/tessdata_best/raw/main/rus.traineddata
# arabian
RUN curl -o ${TESSDATA_PREFIX}/tat.traineddata \
    -H 'Accept: application/vnd.github.v3.raw' \
    -L https://github.com/tesseract-ocr/tessdata_best/raw/main/ara.traineddata
# setup python arguments 
ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.2.2
# install poetry
RUN pip install "poetry==$POETRY_VERSION"
# create workdir directory
RUN mkdir /app
WORKDIR /app
# copy dependencies
COPY poetry.lock pyproject.toml /app/
# install all dependencies
RUN pip3 install "git+https://github.com/openai/whisper.git"
RUN poetry config virtualenvs.create false \
    && poetry install  --only main --no-interaction --no-ansi
# copy code into the workdir
COPY . /app
# execute starting script
RUN mkdir -p /app/temp_data
RUN mkdir -p /app/temp_data/image
RUN mkdir -p /app/temp_data/audio



CMD ["./deploy/standalone.sh"]
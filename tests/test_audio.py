# https://github.com/tiangolo/fastapi/issues/4845 - auth problem
# pytest -s --disable-warnings tests/test_audio.py
# python C:\Users\PodYapolsky\AppData\Local\pypoetry\Cache\virtualenvs\follow-my-reading-2GbujRK9-py3.10\Scripts\huey_consumer.py core.task_system.scheduler -n -k thread
# -s = --capture=no how print statements in console
import os
import uuid
from fastapi.testclient import TestClient

from main import app

DEFAULT_UNEXISTENT_FILE = "01234567-8910-1112-1314-151617181920"
DEFAULT_AUDIO_MODEL = "whisper"


def _register_and_get_token_info(client: TestClient) -> dict[str, str]:
    """Simply combine registration and getting token steps"""
    # try to register of fetch already existed "admin"
    response = client.put("/v1/auth/register?username=admin&password=admin")
    assert response.status_code == 200 or response.status_code == 422

    response = client.post(
        "/v1/auth/token",
        data={
            "grant_type": "",
            "username": "admin",
            "password": "admin",
            "scope": "",
            "client_id": "",
            "client_secret": "",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200  # successful auth

    return response.json()


def _return_headers_with_token(token_info: dict[str, str]):
    """Return a headers pattern to pass auth"""
    return {
        "Accept": "application/json",
        "Authorization": f"{token_info['token_type']} {token_info['access_token']}",
    }


def _is_valid_UUID(string: str) -> bool:
    try:
        uuid.UUID(string)
        return True
    except ValueError:
        return False


def test_general():
    with TestClient(app) as client:
        response = client.post("/v1/audio/upload", data={"upload_file": "some file"})
        assert response.status_code == 401

        response = client.get("/v1/audio/models")
        assert response.status_code == 401

        response = client.post(
            "/v1/audio/process",
            data={
                "audio_file": "some audio file",
                "audio_model": "some model name",
            },
        )
        assert response.status_code == 401

        response = client.get("/v1/audio/download")
        assert response.status_code == 401

        response = client.get("/v1/audio/result")
        assert response.status_code == 401


def test_request_rate_limit():
    with TestClient(app) as client:
        token_info = _register_and_get_token_info(client)

        # try to knock knock 10 times
        for _ in range(10):
            response = client.get(
                "/v1/auth/users/me",
                headers=_return_headers_with_token(token_info),
            )
            assert response.status_code == 200

        # the eleventh one should exceed and raise error
        response = client.get(
            "/v1/auth/users/me",
            headers=_return_headers_with_token(token_info),
        )
        assert response.status_code == 429


def test_upload():
    """
    On testing uploading files:
    https://stackoverflow.com/questions/60783222/how-to-test-a-fastapi-api-endpoint-that-consumes-images
    """
    with TestClient(app) as client:
        filename = "tests/audio/audio.mp3"

        # whether can upload audio if no auth
        response = client.post(
            "/v1/audio/upload",
            files={
                # ! don't know for what the first argument stands for
                "upload_file": (" ", open(filename, "rb"), "audio/mpeg"),
            },
        )
        assert response.status_code == 401

        # authorize and get the token
        token_info = _register_and_get_token_info(client)
        headers = _return_headers_with_token(token_info)

        # payload is not file
        response = client.post(
            "/v1/audio/upload",
            files={
                "upload_file": "not a file",
            },
            headers=headers,
        )
        assert response.status_code == 422

        # file is not audio
        response = client.post(
            "/v1/audio/upload",
            files={
                "upload_file": (" ", open("tests/image/image.jpg", "rb"), "image/jpeg"),
            },
            headers=headers,
        )
        assert response.status_code == 422

        # everything should work
        response = client.post(
            "/v1/audio/upload",
            files={
                "upload_file": (" ", open(filename, "rb"), "audio/mpeg"),
            },
            headers=headers,
        )
        assert response.status_code == 200

        # delete test file from temp_data/audio
        os.remove(f"temp_data/audio/{response.json()['file_id']}")


def test_models():
    with TestClient(app) as client:
        response = client.get("/v1/audio/models")
        assert response.status_code == 401  # if not authenticated

        token_info = _register_and_get_token_info(client)

        response = client.get(
            "/v1/audio/models",
            headers=_return_headers_with_token(token_info),
        )
        assert response.status_code == 200
        models: list[dict] = response.json()["models"]
        assert models != []  # models are not empty
        for model in models:  # models have appropriate type structure
            assert isinstance(model.get("name"), str)
            assert isinstance(model.get("description"), str)

            languages = model.get("languages")
            assert isinstance(languages, list)
            for language in languages:
                assert isinstance(language, str)


def test_process():
    with TestClient(app) as client:
        # no auth
        response = client.post(
            "/v1/audio/process",
            json={
                "audio_file": DEFAULT_UNEXISTENT_FILE,
                "audio_model": DEFAULT_AUDIO_MODEL,
            },
        )
        assert response.status_code == 401

        # authorize and get the token
        token_info = _register_and_get_token_info(client)
        headers = _return_headers_with_token(token_info)

        # upload an audio and get the filename (UUID)
        response = client.post(
            "/v1/audio/upload",
            files={
                "upload_file": (" ", open("tests/audio/audio.mp3", "rb"), "audio/mpeg"),
            },
            headers=headers,
        )
        assert response.status_code == 200
        filename = response.json()["file_id"]

        # model does not exist
        response = client.post(
            "/v1/audio/process",
            json={
                "audio_file": filename,  # definitely exists
                "audio_model": "model that does not exist",
            },
            headers=headers,
        )
        assert response.status_code == 404

        # file does not exist
        response = client.post(
            "/v1/audio/process",
            json={
                "audio_file": DEFAULT_UNEXISTENT_FILE,
                "audio_model": DEFAULT_AUDIO_MODEL,
            },
            headers=headers,
        )
        assert response.status_code == 404

        # wrong format
        response = client.post(
            "/v1/audio/process",
            json={"bruh": "bruh"},
            headers=headers,
        )
        assert response.status_code == 422

        # everything ok
        response = client.post(
            "/v1/audio/process",
            json={
                "audio_file": filename,
                "audio_model": DEFAULT_AUDIO_MODEL,
            },
            headers=headers,
        )
        assert response.status_code == 200
        assert _is_valid_UUID(response.json()["task_id"])

        os.remove(f"temp_data/audio/{filename}")


def test_download():
    with TestClient(app) as client:
        # not auth
        response = client.get("/v1/audio/download?file=bruh")
        assert response.status_code == 401

        # authorize and get the token
        token_info = _register_and_get_token_info(client)
        headers = _return_headers_with_token(token_info)

        # file does not exist
        response = client.get(
            f"/v1/audio/download?file={DEFAULT_UNEXISTENT_FILE}",
            headers=headers,
        )
        assert response.status_code == 404

        # on wrong format
        response = client.get("/v1/audio/download?file=bruh", headers=headers)
        assert response.status_code == 422

        # upload and then try to download
        response = client.post(
            "/v1/audio/upload",
            files={
                "upload_file": (" ", open("tests/audio/audio.mp3", "rb"), "audio/mpeg"),
            },
            headers=headers,
        )
        assert response.status_code == 200

        filename = response.json()["file_id"]

        # everything ok
        response = client.get(f"/v1/audio/download?file={filename}", headers=headers)
        assert response.status_code == 200

        # TODO: path injections

        os.remove(f"temp_data/audio/{filename}")


# def test_result():
#     pass

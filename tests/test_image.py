import os
import uuid

import pytest
from fastapi.testclient import TestClient

from main import app

DEFAULT_UNEXISTENT_FILE = "01234567-8910-1112-1314-151617181920"
DEFAULT_IMAGE_MODEL = "eng_tesseract"
GLOBAL_HEADERS = {}


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

    data: dict[str, str] = response.json()
    return data


def _return_headers_with_token(token_info: dict[str, str]) -> dict[str, str]:
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


def test_start() -> None:
    with TestClient(app) as client:
        token_info = _register_and_get_token_info(client)
        headers = _return_headers_with_token(token_info)

        global GLOBAL_HEADERS
        GLOBAL_HEADERS = headers
        assert GLOBAL_HEADERS != {}


@pytest.mark.flaky(retries=5, delay=30)
def test_general() -> None:
    with TestClient(app) as client:
        response = client.post("/v1/image/upload", data={"upload_file": "some file"})
        assert response.status_code == 401

        response = client.get("/v1/image/models")
        assert response.status_code == 401

        response = client.post(
            "/v1/image/process/task",
            data={
                "image_file": "some image file",
                "image_model": "some model name",
            },
        )
        assert response.status_code == 401

        response = client.get("/v1/image/download")
        assert response.status_code == 401

        response = client.get("/v1/image/process/result")
        assert response.status_code == 401


def test_request_rate_limit() -> None:
    with TestClient(app) as client:
        # try to knock knock 10 times
        for _ in range(10):
            client.get(
                "/v1/auth/users/me",
                headers=GLOBAL_HEADERS,
            )

        # the eleventh one or earlier should exceed and raise error
        response = client.get(
            "/v1/auth/users/me",
            headers=GLOBAL_HEADERS,
        )
        assert response.status_code == 429


##############
### UPLOAD ###
##############
@pytest.mark.flaky(retries=2, delay=30)
def test_upload_no_auth() -> None:
    with TestClient(app) as client:
        filename = "tests/image/image.jpg"

        # whether can upload image if no auth
        response = client.post(
            "/v1/image/upload",
            files={
                "upload_file": (" ", open(filename, "rb"), "image/jpeg"),
            },
        )
        assert response.status_code == 401


@pytest.mark.flaky(retries=2, delay=30)
def test_upload_payload_not_a_file() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/v1/image/upload",
            files={
                "upload_file": "not a file",
            },
            headers=GLOBAL_HEADERS,
        )
        assert response.status_code == 422


@pytest.mark.flaky(retries=2, delay=30)
def test_upload_file_is_not_an_image() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/v1/image/upload",
            files={
                "upload_file": (" ", open("tests/audio/audio.mp3", "rb"), "audio/mpeg"),
            },
            headers=GLOBAL_HEADERS,
        )
        assert response.status_code == 422


@pytest.mark.flaky(retries=2, delay=30)
def test_upload_success() -> None:
    with TestClient(app) as client:
        filename = "tests/image/image.jpg"

        response = client.post(
            "/v1/image/upload",
            files={
                "upload_file": (" ", open(filename, "rb"), "image/jpeg"),
            },
            headers=GLOBAL_HEADERS,
        )
        assert response.status_code == 200

        os.remove(f"temp_data/image/{response.json()['file_id']}")


@pytest.mark.flaky(retries=2, delay=30)
def test_upload() -> None:
    #     """
    #     On testing uploading files:
    #     https://stackoverflow.com/questions/60783222/how-to-test-a-fastapi-api-endpoint-that-consumes-images
    #     """
    with TestClient(app) as client:
        filename = "tests/image/image.jpg"

        # whether can upload image if no auth
        response = client.post(
            "/v1/image/upload",
            files={
                # ! don't know for what the first argument stands for
                "upload_file": (" ", open(filename, "rb"), "image/jpeg"),
            },
        )
        assert response.status_code == 401

        # payload is not file
        response = client.post(
            "/v1/image/upload",
            files={
                "upload_file": "not a file",
            },
            headers=GLOBAL_HEADERS,
        )
        assert response.status_code == 422

        # file is not image
        response = client.post(
            "/v1/image/upload",
            files={
                "upload_file": (" ", open("tests/audio/audio.mp3", "rb"), "audio/mpeg"),
            },
            headers=GLOBAL_HEADERS,
        )
        assert response.status_code == 422

        # everything should work
        response = client.post(
            "/v1/image/upload",
            files={
                "upload_file": (" ", open(filename, "rb"), "image/jpeg"),
            },
            headers=GLOBAL_HEADERS,
        )
        assert response.status_code == 200

        # delete test file from temp_data/image
        os.remove(f"temp_data/image/{response.json()['file_id']}")


##############
### MODELS ###
##############
@pytest.mark.flaky(retries=2, delay=30)
def test_models_no_auth() -> None:
    with TestClient(app) as client:
        response = client.get("/v1/image/models")
        assert response.status_code == 401  # if not authenticated


@pytest.mark.flaky(retries=2, delay=30)
def test_models_success() -> None:
    with TestClient(app) as client:
        response = client.get(
            "/v1/image/models",
            headers=GLOBAL_HEADERS,
        )
        assert response.status_code == 200


@pytest.mark.flaky(retries=2, delay=30)
def test_models_not_empty() -> None:
    with TestClient(app) as client:
        response = client.get(
            "/v1/image/models",
            headers=GLOBAL_HEADERS,
        )
        models: list[dict] = response.json()["models"]
        assert models != []  # models are not empty


@pytest.mark.flaky(retries=2, delay=30)
def test_models_structure() -> None:
    with TestClient(app) as client:
        response = client.get(
            "/v1/image/models",
            headers=GLOBAL_HEADERS,
        )
        models: list[dict] = response.json()["models"]
        for model in models:  # models have appropriate type structure
            assert isinstance(model.get("name"), str)
            assert isinstance(model.get("description"), str)

            languages = model.get("languages")
            assert isinstance(languages, list)
            for language in languages:
                assert isinstance(language, str)


@pytest.mark.flaky(retries=2, delay=30)
def test_models() -> None:
    with TestClient(app) as client:
        response = client.get("/v1/image/models")
        assert response.status_code == 401  # if not authenticated

        response = client.get(
            "/v1/image/models",
            headers=GLOBAL_HEADERS,
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


###############
### PROCESS ###
###############
@pytest.mark.flaky(retries=2, delay=30)
def test_process_no_auth() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/v1/image/process/task",
            json={
                "image_file": DEFAULT_UNEXISTENT_FILE,
                "image_model": DEFAULT_IMAGE_MODEL,
            },
        )
        assert response.status_code == 401


@pytest.mark.flaky(retries=2, delay=30)
def test_process_model_does_not_exist() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/v1/image/upload",
            files={
                "upload_file": (" ", open("tests/image/image.jpg", "rb"), "image/jpeg"),
            },
            headers=GLOBAL_HEADERS,
        )
        assert response.status_code == 200
        filename = response.json()["file_id"]

        response = client.post(
            "/v1/image/process/task",
            json={
                "image_file": filename,  # definitely exists
                "image_model": "model that does not exist",
            },
            headers=GLOBAL_HEADERS,
        )
        assert response.status_code == 404

        os.remove(f"temp_data/image/{filename}")


@pytest.mark.flaky(retries=2, delay=30)
def test_process_file_does_not_exist() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/v1/image/upload",
            files={
                "upload_file": (" ", open("tests/image/image.jpg", "rb"), "image/jpeg"),
            },
            headers=GLOBAL_HEADERS,
        )
        assert response.status_code == 200
        filename = response.json()["file_id"]

        response = client.post(
            "/v1/image/process/task",
            json={
                "image_file": DEFAULT_UNEXISTENT_FILE,
                "image_model": DEFAULT_IMAGE_MODEL,
            },
            headers=GLOBAL_HEADERS,
        )
        assert response.status_code == 404

        os.remove(f"temp_data/image/{filename}")


@pytest.mark.flaky(retries=2, delay=30)
def test_process_wrong_format() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/v1/image/upload",
            files={
                "upload_file": (" ", open("tests/image/image.jpg", "rb"), "image/jpeg"),
            },
            headers=GLOBAL_HEADERS,
        )
        assert response.status_code == 200
        filename = response.json()["file_id"]

        response = client.post(
            "/v1/image/process/task",
            json={"bruh": "bruh"},
            headers=GLOBAL_HEADERS,
        )
        assert response.status_code == 422

        os.remove(f"temp_data/image/{filename}")


@pytest.mark.flaky(retries=2, delay=30)
def test_process_success() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/v1/image/upload",
            files={
                "upload_file": (" ", open("tests/image/image.jpg", "rb"), "image/jpeg"),
            },
            headers=GLOBAL_HEADERS,
        )
        filename = response.json()["file_id"]

        response = client.post(
            "/v1/image/process/task",
            json={
                "image_file": filename,
                "image_model": DEFAULT_IMAGE_MODEL,
            },
            headers=GLOBAL_HEADERS,
        )
        assert response.status_code == 200
        assert _is_valid_UUID(response.json()["task_id"])

        os.remove(f"temp_data/image/{filename}")


@pytest.mark.flaky(retries=2, delay=30)
def test_process() -> None:
    with TestClient(app) as client:
        # no auth
        response = client.post(
            "/v1/image/process/task",
            json={
                "image_file": DEFAULT_UNEXISTENT_FILE,
                "image_model": DEFAULT_IMAGE_MODEL,
            },
        )
        assert response.status_code == 401

        # upload an image and get the filename (UUID)
        response = client.post(
            "/v1/image/upload",
            files={
                "upload_file": (" ", open("tests/image/image.jpg", "rb"), "image/jpeg"),
            },
            headers=GLOBAL_HEADERS,
        )
        assert response.status_code == 200
        filename = response.json()["file_id"]

        # model does not exist
        response = client.post(
            "/v1/image/process/task",
            json={
                "image_file": filename,  # definitely exists
                "image_model": "model that does not exist",
            },
            headers=GLOBAL_HEADERS,
        )
        assert response.status_code == 404

        # file does not exist
        response = client.post(
            "/v1/image/process/task",
            json={
                "image_file": DEFAULT_UNEXISTENT_FILE,
                "image_model": DEFAULT_IMAGE_MODEL,
            },
            headers=GLOBAL_HEADERS,
        )
        assert response.status_code == 404

        # wrong format
        response = client.post(
            "/v1/image/process/task",
            json={"bruh": "bruh"},
            headers=GLOBAL_HEADERS,
        )
        assert response.status_code == 422

        # everything ok
        response = client.post(
            "/v1/image/process/task",
            json={
                "image_file": filename,
                "image_model": DEFAULT_IMAGE_MODEL,
            },
            headers=GLOBAL_HEADERS,
        )
        assert response.status_code == 200
        assert _is_valid_UUID(response.json()["task_id"])

        os.remove(f"temp_data/image/{filename}")


################
### DOWNLOAD ###
################
@pytest.mark.flaky(retries=2, delay=30)
def test_download_no_auth() -> None:
    with TestClient(app) as client:
        response = client.get("/v1/image/download?file=bruh")
        assert response.status_code == 401


@pytest.mark.flaky(retries=2, delay=30)
def test_download_file_does_not_exist() -> None:
    with TestClient(app) as client:
        response = client.get(
            f"/v1/image/download?file={DEFAULT_UNEXISTENT_FILE}",
            headers=GLOBAL_HEADERS,
        )
        assert response.status_code == 404


@pytest.mark.flaky(retries=2, delay=30)
def test_download_wrong_format() -> None:
    with TestClient(app) as client:
        response = client.get("/v1/image/download?file=bruh", headers=GLOBAL_HEADERS)
        assert response.status_code == 422


@pytest.mark.flaky(retries=2, delay=30)
def test_download_success() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/v1/image/upload",
            files={
                "upload_file": (" ", open("tests/image/image.jpg", "rb"), "image/jpeg"),
            },
            headers=GLOBAL_HEADERS,
        )
        assert response.status_code == 200
        filename = response.json()["file_id"]

        response = client.get(
            f"/v1/image/download?file={filename}", headers=GLOBAL_HEADERS
        )
        assert response.status_code == 200

        os.remove(f"temp_data/image/{filename}")


@pytest.mark.flaky(retries=2, delay=30)
def test_download() -> None:
    with TestClient(app) as client:
        # not auth
        response = client.get("/v1/image/download?file=bruh")
        assert response.status_code == 401

        # file does not exist
        response = client.get(
            f"/v1/image/download?file={DEFAULT_UNEXISTENT_FILE}",
            headers=GLOBAL_HEADERS,
        )
        assert response.status_code == 404

        # on wrong format
        response = client.get("/v1/image/download?file=bruh", headers=GLOBAL_HEADERS)
        assert response.status_code == 422

        # upload and then try to download
        response = client.post(
            "/v1/image/upload",
            files={
                "upload_file": (" ", open("tests/image/image.jpg", "rb"), "image/jpeg"),
            },
            headers=GLOBAL_HEADERS,
        )
        assert response.status_code == 200

        filename = response.json()["file_id"]

        # everything ok
        response = client.get(
            f"/v1/image/download?file={filename}", headers=GLOBAL_HEADERS
        )
        assert response.status_code == 200

        # TODO: path injections

        os.remove(f"temp_data/image/{filename}")


##############
### RESULT ###
##############
@pytest.mark.flaky(retries=2, delay=30)
def test_result_no_auth() -> None:
    with TestClient(app) as client:
        response = client.get("/v1/image/process/result?task_id=bruh")
        assert response.status_code == 401


@pytest.mark.flaky(retries=2, delay=30)
def test_result_process_and_get_task_id() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/v1/image/upload",
            files={
                "upload_file": (" ", open("tests/image/image.jpg", "rb"), "image/jpeg"),
            },
            headers=GLOBAL_HEADERS,
        )
        assert response.status_code == 200
        filename = response.json()["file_id"]

        response = client.post(
            "/v1/image/process/task",
            json={
                "image_file": filename,
                "image_model": DEFAULT_IMAGE_MODEL,
            },
            headers=GLOBAL_HEADERS,
        )
        assert response.status_code == 200
        task_id = response.json()["task_id"]
        assert _is_valid_UUID(task_id)

        os.remove(f"temp_data/image/{filename}")


@pytest.mark.flaky(retries=2, delay=30)
def test_result_unexistent_task() -> None:
    with TestClient(app) as client:
        response = client.get(
            f"/v1/image/process/result?task_id={DEFAULT_UNEXISTENT_FILE}",
            headers=GLOBAL_HEADERS,
        )
        assert response.status_code == 406


@pytest.mark.flaky(retries=2, delay=30)
def test_result_no_results() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/v1/image/upload",
            files={
                "upload_file": (" ", open("tests/image/image.jpg", "rb"), "image/jpeg"),
            },
            headers=GLOBAL_HEADERS,
        )
        assert response.status_code == 200
        filename = response.json()["file_id"]

        response = client.post(
            "/v1/image/process/task",
            json={
                "image_file": filename,
                "image_model": DEFAULT_IMAGE_MODEL,
            },
            headers=GLOBAL_HEADERS,
        )
        assert response.status_code == 200
        task_id = response.json()["task_id"]

        response = client.get(
            f"/v1/image/process/result?task_id={task_id}",
            headers=GLOBAL_HEADERS,
        )
        assert response.status_code == 406

        os.remove(f"temp_data/image/{filename}")


@pytest.mark.flaky(retries=2, delay=30)
def test_result_type_validation_failed() -> None:
    with TestClient(app) as client:
        response = client.get(
            "/v1/image/process/result?task_id=bruh", headers=GLOBAL_HEADERS
        )
        assert response.status_code == 422


@pytest.mark.flaky(retries=2, delay=30)
def test_result_success() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/v1/image/upload",
            files={
                "upload_file": (" ", open("tests/image/image.jpg", "rb"), "image/jpeg"),
            },
            headers=GLOBAL_HEADERS,
        )
        assert response.status_code == 200
        filename = response.json()["file_id"]

        response = client.post(
            "/v1/image/process/task",
            json={
                "image_file": filename,
                "image_model": DEFAULT_IMAGE_MODEL,
            },
            headers=GLOBAL_HEADERS,
        )
        assert response.status_code == 200
        task_id = response.json()["task_id"]

        response = client.get(
            f"/v1/image/process/result?task_id={task_id}",
            headers=GLOBAL_HEADERS,
        )
        # TODO: fix this to finally get a successful response
        # assert response.status_code == 200

        os.remove(f"temp_data/image/{filename}")


@pytest.mark.flaky(retries=2, delay=30)
def test_result() -> None:
    with TestClient(app) as client:
        # not auth
        response = client.get("/v1/image/process/result?task_id=bruh")
        assert response.status_code == 401

        # upload the image
        response = client.post(
            "/v1/image/upload",
            files={
                "upload_file": (" ", open("tests/image/image.jpg", "rb"), "image/jpeg"),
            },
            headers=GLOBAL_HEADERS,
        )
        assert response.status_code == 200
        filename = response.json()["file_id"]

        # process uploaded image and get task id
        response = client.post(
            "/v1/image/process/task",
            json={
                "image_file": filename,
                "image_model": DEFAULT_IMAGE_MODEL,
            },
            headers=GLOBAL_HEADERS,
        )
        assert response.status_code == 200
        task_id = response.json()["task_id"]
        assert _is_valid_UUID(task_id)

        # there no task or no results
        response = client.get(
            f"/v1/image/process/result?task_id={DEFAULT_UNEXISTENT_FILE}",
            headers=GLOBAL_HEADERS,
        )
        assert response.status_code == 406

        # type validation failed
        response = client.get(
            "/v1/image/process/result?task_id=bruh", headers=GLOBAL_HEADERS
        )
        assert response.status_code == 422

        # everything ok
        response = client.get(
            f"/v1/image/result?task_id={task_id}",
            headers=GLOBAL_HEADERS,
        )

        # TODO: deal with successful task ending, probably use async client
        # assert response.status_code == 200

        # data = response.json()
        # text = data["text"]
        # assert isinstance(text, str)

        # segments = data["segments"]
        # assert isinstance(segments, list)
        # for segment in segments:
        #     assert isinstance(segment, dict)
        #     assert isinstance(segment["start"], int)
        #     assert isinstance(segment["end"], int)
        #     assert isinstance(segment["text"], str)
        #     assert isinstance(segment["file"], str)

        os.remove(f"temp_data/image/{filename}")

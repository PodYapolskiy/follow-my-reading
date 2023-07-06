# https://github.com/tiangolo/fastapi/issues/4845 - auth problem
# pytest -s --disable-warnings tests/test_audio.py
# python C:\Users\PodYapolsky\AppData\Local\pypoetry\Cache\virtualenvs\follow-my-reading-2GbujRK9-py3.10\Scripts\huey_consumer.py core.task_system.scheduler -n -k thread
# -s = --capture=no how print statements in console
from main import app
from fastapi.testclient import TestClient


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


# def test_process():
#     pass


# def test_download():
#     pass


# def test_result():
#     pass

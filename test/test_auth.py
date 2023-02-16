import camara
import datetime

dummy_calls = []


def setup_method():
    dummy_calls.clear()


def dummy_method(name):
    def interceptor():
        dummy_calls.append(name)
        return None, None

    return interceptor


def test_empty_token_is_expired():
    client = camara.Camara(
        client_id='id',
        client_secret='secret',
    )

    assert client.is_token_expired() is True


def test_correct_seconds_left_given():
    client = camara.Camara(
        client_id='id',
        client_secret='secret',
    )

    client.token = {'expires_at': datetime.datetime.now() + datetime.timedelta(seconds=3)}

    # rounding: time passed between setup and execution
    assert round(client.token_seconds_remaining()) == 3


def test_no_refresh_token_if_time_remaining():
    client = camara.Camara(
        client_id='id',
        client_secret='secret',
    )

    client.token = {'expires_at': datetime.datetime.now() + datetime.timedelta(seconds=3)}
    client.create_access_token = dummy_method("create_access_token")

    client.refresh_token()

    assert len(dummy_calls) == 0
    assert 'create_access_token' not in dummy_calls


def test_refresh_token_if_expired():
    client = camara.Camara(
        client_id='id',
        client_secret='secret',
    )

    client.token = {'expires_at': datetime.datetime.now() + datetime.timedelta(seconds=-13)}
    client.create_access_token = dummy_method("create_access_token")

    client.refresh_token()

    assert 'create_access_token' in dummy_calls


def create_fake_token():
    return {
        "created_at": datetime.datetime.now(),
        "expires_at": datetime.datetime.now() + datetime.timedelta(seconds=10),
        "access_token": "fake_token_data",
    }


def test_authorization_header_added():
    client = camara.Camara(
        client_id='id',
        client_secret='secret',
    )

    client.token = create_fake_token()

    headers = client.get_auth_headers({"key": "value"})

    assert {'Authorization': 'Bearer fake_token_data', 'key': 'value'} == headers

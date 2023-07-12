import camara
import camara.EndpointConfig
import camara.TokenProvider
import datetime

dummy_calls = []


def setup_method():
    dummy_calls.clear()


def dummy_method(name):
    def interceptor():
        dummy_calls.append(name)
        return None, None

    return interceptor


def dummy_camara():
    return camara.Camara(
        config=camara.Config(
            auth_url="localhost:8000",
            qod=camara.EndpointConfig.EndpointConfig(
                client_id="",
                client_secret="",
                base_url=""
            ),
            connectivity=camara.EndpointConfig.EndpointConfig(
                client_id="",
                client_secret="",
                base_url=""
            ),
            location=camara.EndpointConfig.EndpointConfig(
                client_id="",
                client_secret="",
                base_url=""
            ),
            version=-1
        )
    )


def test_empty_token_is_expired():
    client = dummy_camara()

    assert client.qod.token_provider.is_token_expired() is True
    assert client.connectivity.token_provider.is_token_expired() is True
    assert client.location.token_provider.is_token_expired() is True


def test_correct_seconds_left_given():
    client = dummy_camara()

    client.qod.token_provider.token = {'expires_at': datetime.datetime.now() + datetime.timedelta(seconds=3)}

    # rounding: time passed between setup and execution
    assert round(client.qod.token_provider.token_seconds_remaining()) == 3


def test_no_refresh_token_if_time_remaining():
    client = dummy_camara()
    qod = client.qod
    provider = qod.token_provider

    provider.token = {'expires_at': datetime.datetime.now() + datetime.timedelta(seconds=3)}
    provider.create_access_token = dummy_method("create_access_token")

    provider.refresh_token()

    assert len(dummy_calls) == 0
    assert 'create_access_token' not in dummy_calls


def test_refresh_token_if_expired():
    client = dummy_camara()
    qod = client.qod
    provider = qod.token_provider

    provider.token = {'expires_at': datetime.datetime.now() + datetime.timedelta(seconds=-13)}
    provider.create_access_token = dummy_method("create_access_token")

    provider.refresh_token()

    assert 'create_access_token' in dummy_calls


def create_fake_token():
    return {
        "created_at": datetime.datetime.now(),
        "expires_at": datetime.datetime.now() + datetime.timedelta(seconds=10),
        "access_token": "fake_token_data",
    }


def test_authorization_header_added():
    client = dummy_camara()
    qod = client.qod
    provider = qod.token_provider

    provider.token = create_fake_token()

    headers = provider.get_auth_headers({"key": "value"})

    assert {'Authorization': 'Bearer fake_token_data', 'key': 'value'} == headers

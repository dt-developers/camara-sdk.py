import camara


def test_no_reauth():
    _ = camara.Camara(
        client_id='id',
        client_secret='secret',
    )
    assert not 'implemented'


def test_auth_if_expired():
    assert not 'implemented'


def test_auth_if_notset():
    assert not 'implemented'

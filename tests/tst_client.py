import time
import pytest

from mock import patch, Mock

from marketorestpython.client import MarketoClient


@pytest.fixture
def client():
    return MarketoClient('123-FDY-456', 'randomclientid', 'supersecret')


def test_marketo_client(client):
    assert client.host == 'https://123-FDY-456.mktorest.com'
    assert client.client_id == 'randomclientid'
    assert client.client_secret == 'supersecret'
    assert client.API_CALLS_MADE == 0
    assert client.API_LIMIT is None

    client = MarketoClient('123-FDY-456', 'randomclientid', 'supersecret', 20)
    assert client.API_LIMIT == 20


@patch('marketorestpython.client.HttpLib')
def test_api_call(m_http_lib, client):
    get_request_mock = Mock(return_value={
        'access_token': '1234', 'expires_in': 1000, 'scope': '1'
    })
    request_mock = Mock(get=get_request_mock)
    m_http_lib.return_value = request_mock
    args = (1, 2, 3)
    kwargs = {'a': 1, 'b': 2}
    client._api_call('get', '/test', *args, **kwargs)
    get_request_mock.assert_called_with(*(('/test',) + args), **kwargs)
    assert client.API_CALLS_MADE == 1

    limit = 4
    client = MarketoClient('123-FDY-456', 'randomclientid', 'supersecret', limit)
    with pytest.raises(Exception) as excinfo:
        for i in xrange(limit):
            client._api_call('get', '/test', *args, **kwargs)
        assert excinfo.value == {
            'message': 'API Calls exceeded the limit : %s' % limit,
            'code': '416'
        }


@patch('marketorestpython.client.MarketoClient._api_call')
def test_authenticate(m_client_api_call, client):
    m_client_api_call.return_value = None
    with pytest.raises(Exception):
        client.authenticate()

    access_token = "cdf01657-110d-4155-99a7-f986b2ff13a0:int"
    token_type = "bearer"
    expires_in = 3599
    scope = "apis@acmeinc.com"
    m_client_api_call.return_value = {
        "access_token": access_token,
        "token_type": token_type,
        "expires_in": expires_in,
        "scope": scope
    }

    client.authenticate()
    m_client_api_call.assert_called_with(
        'get',
        client.host + '/identity/oauth/token',
        {
            'grant_type': 'client_credentials',
            'client_id': client.client_id,
            'client_secret': client.client_secret,
        }
    )

    assert client.token == access_token
    assert client.token_type == token_type
    assert client.expires_in == expires_in
    assert client.valid_until > time.time()
    assert client.scope == scope

    # credentials should still be valid
    client.authenticate()
    assert m_client_api_call.call_count == 2

    # test error handling
    client = MarketoClient('123-FDY-456', 'randomclientid', 'supersecret')
    m_client_api_call.return_value = {
        'error': 'invalid_client',
        'error_description': 'invalid secret'
    }
    with pytest.raises(Exception) as excinfo:
        client.authenticate()
        assert excinfo.value == 'invalid secret'

import os

import pytest


class Fixtures:
    MOCK_CLOUDFRONT_SECRET = 'some secret'

    @pytest.fixture
    def get_env(self, mocker):
        get_env = mocker.patch.object(os, os.getenv.__name__)

        def stub(variable_name):
            if 'CLOUDFRONT_SECRET' == variable_name:
                return self.MOCK_CLOUDFRONT_SECRET

        get_env.side_effect = stub
        return get_env


class TestHandler(Fixtures):
    MOCK_CONNECTION_ID = 'some connection id'
    MOCK_METHOD_ARN_SANS_ROUTE = 'some arn'
    MOCK_METHOD_ARN = f'{MOCK_METHOD_ARN_SANS_ROUTE}/some specific route'

    def test_handle(self, get_env):
        from src.who_let_the_dogs_out.authorizer import handle
        return_value = handle({
            'requestContext': {
                'connectionId': self.MOCK_CONNECTION_ID
            },
            'methodArn': self.MOCK_METHOD_ARN,
            'headers': {
                'cloudfront-secret': self.MOCK_CLOUDFRONT_SECRET
            }
        }, {})

        assert return_value == {
            'principalId': self.MOCK_CONNECTION_ID,
            'policyDocument': {
                'Version': '2012-10-17',
                'Statement': [
                    {
                        'Action': 'execute-api:Invoke',
                        'Effect': 'Allow',
                        'Resource': f'{self.MOCK_METHOD_ARN_SANS_ROUTE}/*'
                    }
                ]
            },
            'context': {
            }
        }

    def test_handle_secret_not_present(self, get_env):
        from src.who_let_the_dogs_out.authorizer import handle
        with pytest.raises(Exception) as e:
            handle({
                'requestContext': {
                    'connectionId': self.MOCK_CONNECTION_ID
                },
                'methodArn': self.MOCK_METHOD_ARN,
                'headers': {
                }
            }, {})

        assert str(e.value) == 'Unauthorized'

    def test_handle_secret_mismatch(self, get_env):
        from src.who_let_the_dogs_out.authorizer import handle
        with pytest.raises(Exception) as e:
            handle({
                'requestContext': {
                    'connectionId': self.MOCK_CONNECTION_ID
                },
                'methodArn': self.MOCK_METHOD_ARN,
                'headers': {
                    'cloudfront-secret': 'not a match'
                }
            }, {})

        assert str(e.value) == 'Unauthorized'

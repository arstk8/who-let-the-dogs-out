import pytest

from test.who_let_the_dogs_out.common_fixtures import AwsFixtures, BasicPythonFixtures


class TestHandler(AwsFixtures, BasicPythonFixtures):
    MOCK_CONNECTION_ID = 'some connection id'
    MOCK_METHOD_ARN_SANS_ROUTE = 'some arn'
    MOCK_METHOD_ARN = f'{MOCK_METHOD_ARN_SANS_ROUTE}/some specific route'

    def test_handle(self):
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

    def test_handle_secret_not_present(self):
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

    def test_handle_secret_mismatch(self):
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

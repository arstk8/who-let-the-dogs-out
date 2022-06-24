import pytest

from src.who_let_the_dogs_out.api_util.validation import Validator


class Fixtures:

    @pytest.fixture
    def mock_function(self, mocker):
        return mocker.Mock()


class TestHandler(Fixtures):
    MOCK_CONNECTION_ID = 'some id'
    MOCK_NEIGHBOR_GROUP = 'some group'
    MOCK_USERNAME = 'some user'

    def test_passes_validation(self, mock_function):
        event = {'some', 'object'}
        _ = {'some': 'other_object'}
        Validator(mock_function).validate(
            event,
            _,
            {'username': self.MOCK_USERNAME, 'neighborGroup': self.MOCK_NEIGHBOR_GROUP},
            {'username': self.MOCK_USERNAME, 'neighborGroup': self.MOCK_NEIGHBOR_GROUP}
        )
        mock_function.assert_called_once_with(event, _)

    def test_fails_validation_because_no_connection_data(self, mock_function):
        event = {'some', 'object'}
        _ = {'some': 'other_object'}
        result = Validator(mock_function).validate(
            event,
            _,
            {'username': self.MOCK_USERNAME, 'neighborGroup': self.MOCK_NEIGHBOR_GROUP},
            None
        )

        assert result == {
            'statusCode': 403,
            'body': 'User does not match the user for this connection!',
            'headers': {
                'Content-Type': 'application/json'
            }
        }
        mock_function.assert_not_called()

    def test_fails_validation_because_neighbor_group_mismatches(self, mock_function):
        event = {'some', 'object'}
        _ = {'some': 'other_object'}
        result = Validator(mock_function).validate(
            event,
            _,
            {'username': 'not a match', 'neighborGroup': self.MOCK_NEIGHBOR_GROUP},
            {'username': self.MOCK_USERNAME, 'neighborGroup': self.MOCK_NEIGHBOR_GROUP},
        )

        assert result == {
            'statusCode': 403,
            'body': 'User does not match the user for this connection!',
            'headers': {
                'Content-Type': 'application/json'
            }
        }
        mock_function.assert_not_called()

    def test_fails_validation_because_username_mismatches(self, mock_function):
        event = {'some', 'object'}
        _ = {'some': 'other_object'}
        result = Validator(mock_function).validate(
            event,
            _,
            {'username': self.MOCK_USERNAME, 'neighborGroup': 'not a match'},
            {'username': self.MOCK_USERNAME, 'neighborGroup': self.MOCK_NEIGHBOR_GROUP},
        )

        assert result == {
            'statusCode': 403,
            'body': 'User does not match the user for this connection!',
            'headers': {
                'Content-Type': 'application/json'
            }
        }
        mock_function.assert_not_called()

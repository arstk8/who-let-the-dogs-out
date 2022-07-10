import pytest

from src.who_let_the_dogs_out.api_util.user_data import SupplyUserData


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
        SupplyUserData(mock_function).validate(
            event,
            _,
            {'username': self.MOCK_USERNAME, 'neighborGroup': self.MOCK_NEIGHBOR_GROUP}
        )
        mock_function.assert_called_once_with(
            event,
            {'username': self.MOCK_USERNAME, 'neighborGroup': self.MOCK_NEIGHBOR_GROUP}
        )

    def test_fails_validation_because_no_connection_data(self, mock_function):
        event = {'some', 'object'}
        _ = {'some': 'other_object'}
        SupplyUserData(mock_function).validate(
            event,
            _,
            None
        )

        mock_function.assert_called_once_with(
            event,
            None
        )

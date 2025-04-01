from unittest.mock import MagicMock

from controllers.collaborator_controller import get_id_from_enum_role
from utils.permissions import RoleType
from utils.util import choose_from_enum


def test_choose_from_enum(mocker):
    mock_display_message = mocker.patch('views.view.display_message')
    mock_input = mocker.patch('views.view.get_input', return_value="1")
    result = choose_from_enum(RoleType, "Select option")

    assert result == RoleType.MANAGEMENT

    mock_display_message.assert_any_call("Select option:")
    mock_display_message.assert_any_call("1. MANAGEMENT")
    mock_display_message.assert_any_call("2. SALES")
    mock_display_message.assert_any_call("3. SUPPORT")

    mock_input.assert_called_once_with("Enter the number of your choice")


def test_invalid_choose_from_enum(mocker):
    mocker.patch('views.view.display_message')
    mock_input = mocker.patch('views.view.get_input', side_effect=["a", "1"])
    mock_display_error = mocker.patch('views.view.display_error')

    result = choose_from_enum(RoleType, "Select option")

    assert result == RoleType.MANAGEMENT

    assert mock_input.call_count == 2

    mock_display_error.assert_called_once()


def test_out_of_range_choose_from_enum(mocker):
    mocker.patch('views.view.display_message')
    mock_input = mocker.patch('views.view.get_input', side_effect=["4", "1"])
    mock_display_error = mocker.patch('views.view.display_error')

    result = choose_from_enum(RoleType, "Select option")

    assert result == RoleType.MANAGEMENT

    assert mock_input.call_count == 2

    mock_display_error.assert_called_once()


def test_get_id_from_enum_role(mocker, mock_session):
    mock_display_error = mocker.patch('views.view.display_error')
    mock_result = MagicMock()
    mock_result.scalar.return_value = 4
    mock_session.execute.return_value = mock_result


    result = get_id_from_enum_role(RoleType.MANAGEMENT, mock_session)

    assert result == 4

    mock_display_error.assert_not_called()

    mock_session.execute.assert_called_once()


def test_get_id_from_enum_role_not_exist(mocker, mock_session):
    mock_display_error = mocker.patch('views.view.display_error')
    mock_result = MagicMock()
    mock_result.scalar.return_value = None
    mock_session.execute.return_value = mock_result

    result = get_id_from_enum_role(RoleType.MANAGEMENT, mock_session)

    assert result is None

    mock_display_error.assert_called_once_with(f"Role {RoleType.MANAGEMENT.value} not "
                                               f"found in collaborator_role.")





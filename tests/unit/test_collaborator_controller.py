from unittest.mock import patch

from controllers.collaborator_controller import get_id_from_enum_role
from utils.permissions import RoleType


@patch("controllers.collaborator_controller.Session")
def test_get_id_from_enum_role(mock_session):
    mock_result = mock_session.return_value.execute.return_value
    mock_result.scalar.return_value = 4

    result = get_id_from_enum_role(RoleType.MANAGEMENT, mock_session.return_value)

    assert result == 4
    mock_session.return_value.execute.assert_called_once()


@patch("controllers.collaborator_controller.Session")
@patch("views.view.display_error")
def test_get_id_from_enum_role_not_exist(mock_display_error, mock_session):
    mock_result = mock_session.return_value.execute.return_value
    mock_result.scalar.return_value = None

    result = get_id_from_enum_role(RoleType.MANAGEMENT, mock_session.return_value)

    assert result is None
    mock_display_error.assert_called_once_with(
        f"Role {RoleType.MANAGEMENT.value} not " f"found in collaborator_role."
    )

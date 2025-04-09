from unittest.mock import patch

from controllers.collaborator_controller import (
    create_collaborator,
    update_collaborator,
    delete_collaborator,
    login,
    logout,
)
from models.collaborator import Collaborator
from utils.permissions import RoleType


def test_create_collaborator_success(runner, db_session, roles, management_user):
    """Test creating a collaborator."""
    management_role = next(r for r in roles if r.name == RoleType.MANAGEMENT)

    with patch(
        "controllers.collaborator_controller.Session", return_value=db_session
    ), patch(
        "controllers.collaborator_controller.util.ask_for_input",
        side_effect=[
            "new@collaborator.com",
            "0123456781",
            "New",
            "Collaborator",
        ],
    ), patch(
        "controllers.collaborator_controller.util.ask_for_password",
        side_effect=["password123!"],
    ), patch(
        "controllers.event_controller.util.get_token",
        return_value={"role": "management", "id": management_user.id},
    ), patch(
        "controllers.collaborator_controller.util.choose_from_enum",
        return_value=RoleType.MANAGEMENT,
    ), patch(
        "controllers.collaborator_controller.get_id_from_enum_role",
        return_value=management_role.id,
    ):
        result = runner.invoke(create_collaborator)
        assert result.exit_code == 0

        collaborator = (
            db_session.query(Collaborator)
            .filter_by(email="new@collaborator.com")
            .first()
        )
        assert collaborator is not None
        assert collaborator.first_name == "Collaborator"
        assert collaborator.name == "New"
        assert collaborator.phone_number == "0123456781"
        assert collaborator.role_id == management_role.id


def test_create_collaborator_duplicate_email(runner, db_session, management_user):
    """Test creating a collaborator with an existing email."""
    with patch(
        "controllers.collaborator_controller.Session", return_value=db_session
    ), patch(
        "controllers.event_controller.util.get_token",
        return_value={"role": "management", "id": management_user.id},
    ), patch(
        "controllers.collaborator_controller.util.ask_for_input",
        return_value=management_user.email,
    ), patch(
        "controllers.collaborator_controller.view.display_error"
    ) as mock_display_error:
        result = runner.invoke(create_collaborator)

        assert result.exit_code == 0
        mock_display_error.assert_called_once_with(
            "This email or phone number already exists."
        )


def test_update_collaborator_success(runner, db_session, management_user):
    """Test updating a collaborator."""

    with patch(
        "controllers.collaborator_controller.Session", return_value=db_session
    ), patch(
        "controllers.collaborator_controller.util.get_token",
        return_value={"role": "management", "id": management_user.id},
    ), patch(
        "controllers.collaborator_controller.util.ask_for_input",
        side_effect=[management_user.email, "Updated"],
    ), patch(
        "controllers.collaborator_controller.view.display_edit_collaborator",
        return_value="1",
    ):
        result = runner.invoke(update_collaborator)

        assert result.exit_code == 0
        assert management_user.first_name == "Updated"


def test_update_collaborator_not_found(runner, db_session, management_user):
    """Test updating a non-existent collaborator."""
    with patch(
        "controllers.collaborator_controller.Session", return_value=db_session
    ), patch(
        "controllers.collaborator_controller.util.get_token",
        return_value={"role": "management", "id": management_user.id},
    ), patch(
        "controllers.collaborator_controller.util.ask_for_input",
        return_value="nonexistent@email.com",
    ), patch(
        "controllers.collaborator_controller.view.display_error"
    ) as mock_display_error:
        result = runner.invoke(update_collaborator)

        assert result.exit_code == 0
        mock_display_error.assert_called_once_with("No collaborator found.")


def test_delete_collaborator_success(runner, db_session, management_user, sales_user):
    """Test deleting a collaborator."""

    with patch(
        "controllers.collaborator_controller.Session", return_value=db_session
    ), patch(
        "controllers.collaborator_controller.util.get_token",
        return_value={"role": "management", "id": management_user.id},
    ), patch(
        "controllers.collaborator_controller.util.ask_for_input",
        side_effect=[sales_user.email, "y"],
    ):
        result = runner.invoke(delete_collaborator)

        assert result.exit_code == 0
        deleted_collaborator = (
            db_session.query(Collaborator).filter_by(email=sales_user.email).first()
        )
        assert deleted_collaborator is None


def test_delete_collaborator_not_found(runner, db_session, management_user):
    """Test deleting a non-existent collaborator."""
    with patch(
        "controllers.collaborator_controller.Session", return_value=db_session
    ), patch(
        "controllers.collaborator_controller.util.get_token",
        return_value={"role": "management", "id": management_user.id},
    ), patch(
        "controllers.collaborator_controller.util.ask_for_input",
        return_value="nonexistent@email.com",
    ), patch(
        "controllers.collaborator_controller.view.display_error"
    ) as mock_display_error:
        result = runner.invoke(delete_collaborator)

        assert result.exit_code == 0
        mock_display_error.assert_called_once_with("No collaborator found.")


def test_login_success(runner, db_session, management_user):
    """Test successful login."""
    with patch(
        "controllers.collaborator_controller.Session", return_value=db_session
    ), patch(
        "controllers.collaborator_controller.util.ask_for_input",
        side_effect=[management_user.email],
    ), patch(
        "controllers.collaborator_controller.util.ask_for_password",
        side_effect=["password123!"],
    ), patch(
        "controllers.collaborator_controller.util.hash_password",
        return_value=management_user.password,
    ), patch(
        "controllers.collaborator_controller.util.create_token"
    ) as mock_save_token:
        result = runner.invoke(login)

        assert result.exit_code == 0
        mock_save_token.assert_called_once()


def test_login_invalid_credentials(runner, db_session, management_user):
    """Test login with invalid credentials."""
    with patch(
        "controllers.collaborator_controller.Session", return_value=db_session
    ), patch(
        "controllers.collaborator_controller.util.ask_for_input",
        side_effect=[management_user.email],
    ), patch(
        "controllers.collaborator_controller.util.ask_for_password",
        side_effect=["wrongpassword"],
    ), patch(
        "controllers.collaborator_controller.util.hash_password",
        return_value="wrong_hash",
    ), patch(
        "controllers.collaborator_controller.view.display_error"
    ) as mock_display_error:
        result = runner.invoke(login)

        assert result.exit_code == 0
        mock_display_error.assert_called_once_with("Incorrect password.")


def test_logout_success(runner):
    """Test logout."""
    with patch(
        "controllers.collaborator_controller.util.delete_token"
    ) as mock_delete_token, patch(
        "controllers.collaborator_controller.view.display_message"
    ) as mock_display_message:
        result = runner.invoke(logout)

        assert result.exit_code == 0
        mock_delete_token.assert_called_once()
        mock_display_message.assert_called_once_with("Logout successful.", "green")

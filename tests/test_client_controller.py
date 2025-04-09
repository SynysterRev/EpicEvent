from unittest.mock import patch

from controllers.client_controller import (
    get_clients,
    create_client,
    update_client,
)
from models.client import Client


def test_get_clients_success(runner, db_session, management_user, test_client):
    """Test retrieving clients with a management user."""
    with patch("controllers.client_controller.Session", return_value=db_session), patch(
        "controllers.client_controller.util.get_token",
        return_value={"role": "management", "id": management_user.id},
    ):
        result = runner.invoke(get_clients)
        assert result.exit_code == 0
        assert str(test_client) in result.output


def test_get_clients_with_filters(runner, db_session, sales_user, test_client):
    """Test retrieving clients with filters for a sales user."""
    with patch("controllers.client_controller.Session", return_value=db_session), patch(
        "controllers.client_controller.util.get_token",
        return_value={"role": "sales", "id": sales_user.id},
    ):
        result = runner.invoke(get_clients, ["--assigned"])

        assert result.exit_code == 0
        assert str(test_client) in result.output


def test_create_client_success(runner, db_session, sales_user):
    """Test creating a client."""
    sales_user_id = sales_user.id

    with patch("controllers.client_controller.Session", return_value=db_session), patch(
        "controllers.client_controller.util.get_token",
        return_value={"role": "sales", "id": sales_user_id},
    ), patch(
        "controllers.client_controller.util.ask_for_input",
        side_effect=[
            "Test Client",
            "test@client.com",
            "0123456789",
            "Test Company",
            str(sales_user_id),
        ],
    ):
        result = runner.invoke(create_client)

        assert result.exit_code == 0

        client = db_session.query(Client).filter_by(email="test@client.com").first()
        assert client is not None
        assert client.full_name == "Test Client"
        assert client.phone_number == "0123456789"
        assert client.company == "Test Company"
        assert client.sales_contact_id == sales_user_id


def test_update_client_success(runner, db_session, sales_user, test_client):
    """Test updating a client."""

    with patch("controllers.client_controller.Session", return_value=db_session), patch(
        "controllers.client_controller.util.get_token",
        return_value={"role": "sales", "id": sales_user.id},
    ), patch(
        "controllers.client_controller.util.ask_for_input",
        side_effect=[test_client.email, "Updated company"],
    ), patch(
        "controllers.client_controller.view.display_edit_client", return_value="4"
    ):
        result = runner.invoke(update_client)

        assert result.exit_code == 0
        assert test_client.company == "Updated company"


def test_update_client_not_found(runner, db_session, sales_user):
    """Test updating a non-existent client."""
    with patch("controllers.client_controller.Session", return_value=db_session), patch(
        "controllers.client_controller.util.get_token",
        return_value={"role": "sales", "id": sales_user.id},
    ), patch(
        "controllers.client_controller.util.ask_for_input",
        return_value="nonexistent@email.com",
    ), patch(
        "controllers.client_controller.view.display_error"
    ) as mock_display_error:
        result = runner.invoke(update_client)

        assert result.exit_code == 0
        mock_display_error.assert_called_once_with("No client found.")

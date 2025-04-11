from unittest.mock import patch

from controllers.contract_controller import (
    get_contracts,
    create_contract,
    update_contract,
)
from models.collaborator import Collaborator
from models.contract import Contract, Status


def test_get_contracts_success(runner, db_session, management_user, test_contract):
    """Test retrieving contracts with a management user."""
    with patch(
        "controllers.contract_controller.Session", return_value=db_session
    ), patch(
        "controllers.contract_controller.util.get_token",
        return_value={"role": "management", "id": management_user.id},
    ):
        result = runner.invoke(get_contracts)
        assert result.exit_code == 0
        assert str(test_contract) in result.output


def test_get_contracts_with_filters(runner, db_session, sales_user, test_contract):
    """Test retrieving contracts with filters for a sales user."""
    with patch(
        "controllers.contract_controller.Session", return_value=db_session
    ), patch(
        "controllers.contract_controller.util.get_token",
        return_value={"role": "sales", "id": sales_user.id},
    ):
        result = runner.invoke(get_contracts, ["--assigned"])

        assert result.exit_code == 0
        assert str(test_contract) in result.output


def test_get_contracts_with_status_filter(
    runner, db_session, management_user, test_contract
):
    """Test retrieving contracts with a status filter."""
    with patch(
        "controllers.contract_controller.Session", return_value=db_session
    ), patch(
        "controllers.contract_controller.util.get_token",
        return_value={"role": "management", "id": management_user.id},
    ):
        result = runner.invoke(get_contracts, ["--status", "signed"])

        assert result.exit_code == 0
        assert str(test_contract) in result.output


def test_create_contract_success(
    runner, db_session, management_user, test_client, sales_user
):
    """Test creating a contract."""
    management_user_id = management_user.id
    client_id = test_client.id
    sales_user_id = sales_user.id

    with patch(
        "controllers.contract_controller.Session", return_value=db_session
    ), patch(
        "controllers.contract_controller.util.get_token",
        return_value={"role": "management", "id": management_user_id},
    ), patch(
        "controllers.contract_controller.util.ask_for_input",
        side_effect=[
            str(client_id),
            "1000.00",
            "500.00",
        ],
    ), patch(
        "controllers.contract_controller.util.choose_from_enum",
        return_value=Status.SIGNED,
    ):
        result = runner.invoke(create_contract)

        assert result.exit_code == 0

        contract = db_session.query(Contract).filter_by(client_id=client_id).first()
        assert contract is not None
        assert contract.total_amount == 1000.0
        assert contract.remaining_amount == 500.0
        assert contract.status == Status.SIGNED
        assert contract.sales_contact_id == sales_user_id


def test_create_contract_client_not_found(runner, db_session, management_user):
    """Test creating a contract with a non-existent client."""
    with patch(
        "controllers.contract_controller.Session", return_value=db_session
    ), patch(
        "controllers.contract_controller.util.get_token",
        return_value={"role": "management", "id": management_user.id},
    ), patch(
        "controllers.contract_controller.util.ask_for_input", return_value="999"
    ), patch(
        "controllers.contract_controller.view.display_error"
    ) as mock_display_error:
        result = runner.invoke(create_contract)

        assert result.exit_code == 0
        mock_display_error.assert_called_once_with("Client with id 999 does not exist.")


def test_update_contract_success(runner, db_session, management_user, test_contract):
    """Test updating a contract."""

    with patch(
        "controllers.contract_controller.Session", return_value=db_session
    ), patch(
        "controllers.contract_controller.util.get_token",
        return_value={"role": "management", "id": management_user.id},
    ), patch(
        "controllers.contract_controller.util.ask_for_input",
        side_effect=[str(test_contract.id), "1", 2000.0],
    ), patch(
        "controllers.contract_controller.view.display_edit_contract", return_value="1"
    ):
        result = runner.invoke(update_contract)

        assert result.exit_code == 0
        assert test_contract.total_amount == 2000.0


def test_update_contract_not_found(runner, db_session, management_user):
    """Test updating a non-existent contract."""
    with patch(
        "controllers.contract_controller.Session", return_value=db_session
    ), patch(
        "controllers.contract_controller.util.get_token",
        return_value={"role": "management", "id": management_user.id},
    ), patch(
        "controllers.contract_controller.util.ask_for_input", return_value="999"
    ), patch(
        "controllers.contract_controller.view.display_error"
    ) as mock_display_error:
        result = runner.invoke(update_contract)

        assert result.exit_code == 0
        mock_display_error.assert_called_once_with(
            "Contract with id 999 does not exist."
        )


def test_update_contract_not_authorized(runner, db_session, test_contract):
    """Test updating a contract by an unauthorized user."""

    other_sales = Collaborator(
        email="other@test.com",
        password="password123!",
        first_name="Other",
        name="Sales",
        phone_number="0123456785",
        role=test_contract.collaborator.role,
    )
    db_session.add(other_sales)
    db_session.commit()

    with patch(
        "controllers.contract_controller.Session", return_value=db_session
    ), patch(
        "controllers.contract_controller.util.get_token",
        return_value={"role": "sales", "id": other_sales.id},
    ), patch(
        "controllers.contract_controller.util.ask_for_input",
        return_value=str(test_contract.id),
    ), patch(
        "controllers.contract_controller.view.display_edit_contract", return_value="0"
    ), patch(
        "controllers.contract_controller.view.display_error"
    ) as mock_display_error:
        result = runner.invoke(update_contract)

        assert result.exit_code == 0
        mock_display_error.assert_called_once_with(
            "You are not authorized to update an contract to which you are not assigned."
        )

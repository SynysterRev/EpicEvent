from datetime import date, time
from unittest.mock import patch

from controllers.event_controller import (
    get_events,
    create_event,
    update_event,
)
from models.collaborator import Collaborator
from models.contract import Status
from models.event import Event
from utils.permissions import RoleType


def test_get_events_success(runner, db_session, management_user, test_event):
    """Test retrieving events with a management user."""
    with patch("controllers.event_controller.Session", return_value=db_session), patch(
        "controllers.event_controller.util.get_token",
        return_value={"role": "management", "id": management_user},
    ):
        result = runner.invoke(get_events)
        assert result.exit_code == 0
        assert str(test_event) in result.output


def test_get_events_with_filters(runner, db_session, support_user, test_event):
    """Test retrieving events with filters for a support user."""
    with patch("controllers.event_controller.Session", return_value=db_session), patch(
        "controllers.event_controller.util.get_token",
        return_value={"role": "support", "id": support_user.id},
    ):
        result = runner.invoke(get_events, ["--assign", "assigned"])

        assert result.exit_code == 0
        assert str(test_event) in result.output


def test_create_event_success(
    runner, db_session, sales_user, test_contract, support_user
):
    """Test creating an event."""
    sales_user_id = sales_user.id
    contract_id = test_contract.id
    support_user_id = support_user.id

    with patch("controllers.event_controller.Session", return_value=db_session), patch(
        "controllers.event_controller.util.get_token",
        return_value={"role": "sales", "id": sales_user_id},
    ), patch(
        "controllers.event_controller.util.ask_for_input",
        side_effect=[
            str(contract_id),
            "2024-02-01",
            "10:00",
            "2024-02-01",
            "18:00",
            "Nouvelle Location",
            "20",
            str(support_user_id),
        ],
    ):
        result = runner.invoke(create_event)

        assert result.exit_code == 0

        event = db_session.query(Event).filter_by(location="Nouvelle Location").first()
        assert event is not None
        assert event.contract_id == contract_id
        assert event.support_contact_id == support_user_id
        assert event.attendees == 20
        assert event.start_time == time(10, 0)
        assert event.end_time == time(18, 0)


def test_create_event_contract_not_found(runner, db_session, sales_user):
    """Test creating an event with a non-existent contract."""
    with patch("controllers.event_controller.Session", return_value=db_session), patch(
        "controllers.event_controller.util.get_token",
        return_value={"role": "sales", "id": sales_user},
    ), patch(
        "controllers.event_controller.util.ask_for_input", return_value="999"
    ), patch(
        "controllers.event_controller.view.display_error"
    ) as mock_display_error:
        result = runner.invoke(create_event)

        assert result.exit_code == 0
        mock_display_error.assert_called_once_with(
            "Contract with id 999 does not exist."
        )


def test_create_event_contract_not_signed(
    runner, db_session, sales_user, test_contract, support_user
):
    """Test creating an event with a non-signed contract."""
    test_contract.status = Status.PENDING
    db_session.commit()

    with patch("controllers.event_controller.Session", return_value=db_session), patch(
        "controllers.event_controller.util.get_token",
        return_value={"role": "sales", "id": sales_user.id},
    ), patch(
        "controllers.event_controller.util.ask_for_input",
        return_value=str(test_contract.id),
    ), patch(
        "controllers.event_controller.view.display_error"
    ) as mock_display_error:
        result = runner.invoke(create_event)

        assert result.exit_code == 0
        mock_display_error.assert_called_once_with(
            "The contract must be signed in order to create events."
        )


def test_update_event_success(runner, db_session, management_user, test_event):
    """Test updating an event."""

    with patch("controllers.event_controller.Session", return_value=db_session), patch(
        "controllers.event_controller.util.get_token",
        return_value={"role": "management", "id": management_user.id},
    ), patch(
        "controllers.event_controller.util.ask_for_input",
        side_effect=[str(test_event.id), "2020-03-01"],
    ), patch(
        "controllers.event_controller.view.display_edit_event", return_value="1"
    ):
        result = runner.invoke(update_event)

        assert result.exit_code == 0
        assert test_event.start_date == str(date(2020, 3, 1))


def test_update_event_not_found(runner, db_session, management_user):
    """Test updating a non-existent event."""
    with patch("controllers.event_controller.Session", return_value=db_session), patch(
        "controllers.event_controller.util.get_token",
        return_value={"role": "management", "id": management_user.id},
    ), patch(
        "controllers.event_controller.util.ask_for_input", return_value="999"
    ), patch(
        "controllers.event_controller.view.display_error"
    ) as mock_display_error:
        result = runner.invoke(update_event)

        assert result.exit_code == 0
        mock_display_error.assert_called_once_with("Event with id 999 does not exist.")


def test_update_event_not_authorized(
    runner, db_session, support_user, test_event
):
    """Test updating an event by an unauthorized user."""
    other_support = Collaborator(
        email="other@test.com",
        password="password123!",
        first_name="Other",
        name="Support",
        phone_number="0123456785",
        role=RoleType.SUPPORT,
    )
    db_session.add(other_support)
    db_session.commit()

    with patch("controllers.event_controller.Session", return_value=db_session), patch(
        "controllers.event_controller.util.get_token",
        return_value={"role": "support", "id": other_support.id},
    ), patch(
        "controllers.event_controller.util.ask_for_input",
        return_value=str(test_event.id),
    ), patch(
        "controllers.event_controller.view.display_edit_event", return_value="0"
    ), patch(
        "controllers.event_controller.view.display_error"
    ) as mock_display_error:
        result = runner.invoke(update_event)

        assert result.exit_code == 0
        mock_display_error.assert_called_once_with(
            "You are not authorized to update an event to which you are not assigned."
        )

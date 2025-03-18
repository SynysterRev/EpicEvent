from datetime import datetime, timezone, timedelta
from unittest.mock import mock_open, MagicMock

import argon2
import jwt
import pytest
from argon2 import PasswordHasher
from jwt import ExpiredSignatureError

from utils.permissions import RoleType
from utils.util import (validate_name, validate_email, verify_password,
                        hash_password, validate_phone_number, validate_password,
                        ask_for_input, ask_for_password, write_env_variable,
                        create_token, get_token)


def test_hash_password():
    password = "azerty123"
    hashed_password = hash_password(password)

    assert password != hashed_password
    assert len(hashed_password) > 0

    ph = PasswordHasher()
    assert ph.verify(hashed_password, password) is True


def test_verify_password():
    password = "azerty123"
    hashed_password = hash_password(password)

    assert verify_password(password, hashed_password) is True


def test_verify_password_invalid():
    password = "azerty123"
    hashed_password = hash_password(password)

    with pytest.raises(argon2.exceptions.VerifyMismatchError) as e:
        verify_password("azert123", hashed_password)
    assert str(e.value) == "The password does not match the supplied hash"


def test_validate_email():
    email = "test@est.com"
    assert validate_email(email) is True


def test_validate_email_invalid():
    email = "test@test"
    with pytest.raises(ValueError) as e:
        validate_email(email)
    assert str(e.value) == "Invalid email address."


def test_validate_name():
    name = "Jean"
    assert validate_name(name) is True


def test_validate_name_invalid():
    name = "1596a"
    with pytest.raises(ValueError) as e:
        validate_name(name)
    assert str(e.value) == ("Your name must be at least 1 character long "
                            "and only contains letters and -.")


def test_validate_phone():
    phone = "0711111111"
    assert validate_phone_number(phone) is True

    phone = "12345678"
    assert validate_phone_number(phone) is True


def test_validate_phone_invalid():
    phone = "1596a"
    with pytest.raises(ValueError) as e:
        validate_phone_number(phone)
    assert str(e.value) == "Your phone number must be at least 8 digits long."

    phone = "0123456"
    with pytest.raises(ValueError) as e:
        validate_phone_number(phone)
    assert str(e.value) == "Your phone number must be at least 8 digits long."


def test_validate_password():
    password = "Azerty123!"
    assert validate_password(password) is True


def test_validate_password_invalid():
    password = "azerty123!"
    with pytest.raises(ValueError) as e:
        validate_password(password)
    assert str(e.value) == (
        "Your password must be at least 8 characters long, contains "
        "at least one uppercase letter, at least one lowercase "
        "letter, at least one number, and at least one special character.")

    password = "Azerty123"
    with pytest.raises(ValueError) as e:
        validate_password(password)
    assert str(e.value) == (
        "Your password must be at least 8 characters long, contains "
        "at least one uppercase letter, at least one lowercase "
        "letter, at least one number, and at least one special character.")

    password = "Azerty!"
    with pytest.raises(ValueError) as e:
        validate_password(password)
    assert str(e.value) == (
        "Your password must be at least 8 characters long, contains "
        "at least one uppercase letter, at least one lowercase "
        "letter, at least one number, and at least one special character.")

    password = "Aze123!"
    with pytest.raises(ValueError) as e:
        validate_password(password)
    assert str(e.value) == (
        "Your password must be at least 8 characters long, contains "
        "at least one uppercase letter, at least one lowercase "
        "letter, at least one number, and at least one special character.")


def test_ask_for_input(mocker):
    mock_input = mocker.patch('views.view.get_input', return_value="name")
    result = ask_for_input("Enter input")

    assert result == "name"

    mock_input.assert_called_once()


def test_ask_for_input_with_function(mocker):
    mock_input = mocker.patch('views.view.get_input', return_value="name")
    result = ask_for_input("Enter input", validate_name)

    assert result == "name"

    mock_input.assert_called_once()


def test_ask_for_input_with_function_invalid(mocker):
    mock_input = mocker.patch('views.view.get_input', side_effect=["name",
                                                                   "Azerty123!"])
    mock_display_error = mocker.patch('views.view.display_error')
    result = ask_for_input("Enter input", validate_password)

    assert result == "Azerty123!"

    assert mock_input.call_count == 2

    mock_display_error.assert_called_once()


def test_ask_for_password(mocker):
    mock_input = mocker.patch('views.view.get_password', return_value="name")
    result = ask_for_password("Enter password")

    assert result == "name"

    mock_input.assert_called_once()


def test_ask_for_password_with_function(mocker):
    mock_input = mocker.patch('views.view.get_password', return_value="Azerty123!")
    result = ask_for_password("Enter password", validate_password)

    assert result == "Azerty123!"

    mock_input.assert_called_once()


def test_ask_for_password_with_function_invalid(mocker):
    mock_input = mocker.patch('views.view.get_password', side_effect=["name",
                                                                      "Azerty123!"])
    mock_display_error = mocker.patch('views.view.display_error')
    result = ask_for_password("Enter password", validate_password)

    assert result == "Azerty123!"

    assert mock_input.call_count == 2

    mock_display_error.assert_called_once()


def test_write_env_var(mocker):
    mocker.patch('os.path.exists', return_value=False)

    mock_file = mock_open()
    mocker.patch('builtins.open', mock_file)

    mock_reload = mocker.patch('db_config.reload_env')

    write_env_variable('NEW_VAR', 'new_value')

    mock_file.assert_called_with('.env', 'w')

    handle = mock_file()
    expected_content = ["NEW_VAR='new_value'\n"]
    handle.writelines.assert_called_once_with(expected_content)


def test_write_env_var_new_variable(mock_env_file, mocker):
    mocker.patch('os.path.exists', return_value=True)

    mock_file = mock_open(read_data=''.join(mock_env_file))
    mocker.patch('builtins.open', mock_file)

    mock_reload = mocker.patch('db_config.reload_env')

    write_env_variable('NEW_VAR', 'new_value')

    mock_file.assert_any_call('.env', 'r')
    mock_file.assert_any_call('.env', 'w')

    handle = mock_file()
    expected_content = [
        "EXISTING_VAR='existing_value'\n",
        "ANOTHER_VAR='another_value'\n",
        "NEW_VAR='new_value'\n"
    ]
    handle.writelines.assert_called_once_with(expected_content)


def test_write_env_var_update_variable(mock_env_file, mocker):
    mocker.patch('os.path.exists', return_value=True)

    mock_file = mock_open(read_data=''.join(mock_env_file))
    mocker.patch('builtins.open', mock_file)

    mock_reload = mocker.patch('db_config.reload_env')

    write_env_variable('EXISTING_VAR', 'updated_value')

    handle = mock_file()
    expected_content = [
        "EXISTING_VAR='updated_value'\n",
        "ANOTHER_VAR='another_value'\n"
    ]
    handle.writelines.assert_called_once_with(expected_content)


def test_write_env_var_exception(mocker):
    mocker.patch('os.path.exists', return_value=True)
    mocker.patch('builtins.open', side_effect=Exception)

    with pytest.raises(Exception) as excinfo:
        write_env_variable('TEST_VAR', 'test_value')

    assert f"Error writing to '.env': {str(excinfo)}"


def test_create_token(mocker):
    secret_key = 'secret_key'
    mocker.patch('utils.util.SECRET_KEY', secret_key)
    collaborator = MagicMock()
    collaborator.first_name = "bob"
    collaborator.name = "bob"
    collaborator.role.name.value = RoleType.MANAGEMENT.value

    mock_write = mocker.patch("utils.util.write_env_variable")

    token = create_token(collaborator)

    payload = jwt.decode(token, secret_key, algorithms=["HS256"])
    assert payload["first_name"] == "bob"
    assert payload["name"] == "bob"
    assert payload["role"] == RoleType.MANAGEMENT.value
    assert "exp" in payload

    mock_write.assert_called_once_with("TOKEN", token)


def test_create_token_invalid(mocker):
    secret_key = None
    mocker.patch('utils.util.SECRET_KEY', secret_key)
    collaborator = MagicMock()

    mock_write = mocker.patch("utils.util.write_env_variable")
    with pytest.raises(ValueError) as e:
        token = create_token(collaborator)

    assert "SECRET_KEY not found in environment variables. Use the init command first."


def test_get_token(mocker):
    secret_key = 'secret_key'
    mocker.patch('utils.util.SECRET_KEY', secret_key)
    payload = {
        "first_name": "bob",
        "name": "bob",
        "role": "management",
        "exp": datetime.now(tz=timezone.utc) + timedelta(minutes=15)
    }

    fake_token = jwt.encode(payload, secret_key, algorithm="HS256")
    mocker.patch('utils.util.TOKEN', fake_token)

    token = get_token()

    assert token["first_name"] == "bob"
    assert token["name"] == "bob"
    assert token["role"] == "management"
    assert "exp" in token


def test_get_token_missing_secret_key(mocker):
    secret_key = None
    mocker.patch('utils.util.SECRET_KEY', secret_key)

    with pytest.raises(ValueError) as e:
        token = get_token()

    assert "SECRET_KEY not found in environment variables. Use the init command first."


def test_get_token_expired(mocker):
    secret_key = 'secret_key'
    mocker.patch('utils.util.SECRET_KEY', secret_key)
    payload = {
        "first_name": "bob",
        "name": "bob",
        "role": "management",
        "exp": datetime.now(tz=timezone.utc) - timedelta(minutes=15)
    }

    fake_token = jwt.encode(payload, secret_key, algorithm="HS256")
    mocker.patch('utils.util.TOKEN', fake_token)

    with pytest.raises(ExpiredSignatureError) as e:
        token = get_token()

    assert "Token expired. Please log in again."


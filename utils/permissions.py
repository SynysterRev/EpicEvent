import enum
import functools
from copy import deepcopy

import sentry_sdk

from utils import util
from views import view


class RoleType(enum.Enum):
    MANAGEMENT = "management"
    SALES = "sales"
    SUPPORT = "support"


class ActionType(enum.Enum):
    CREATE = "create"
    READ = "read"
    UPDATE_ALL = "update_all"
    UPDATE_MINE = "update_mine"
    DELETE = "delete"


class ResourceType(enum.Enum):
    EVENT = "event"
    CONTRACT = "contract"
    CLIENT = "client"
    COLLABORATOR = "collaborator"


class PermissionManager:
    BASE_PERMISSIONS = {
        ActionType.READ: [
            ResourceType.EVENT,
            ResourceType.CONTRACT,
            ResourceType.CLIENT,
            ResourceType.COLLABORATOR,
        ],
        ActionType.CREATE: [],
        ActionType.UPDATE_ALL: [],
        ActionType.UPDATE_MINE: [],
        ActionType.DELETE: [],
    }

    PERMISSIONS = {
        RoleType.MANAGEMENT: {
            ActionType.CREATE: [ResourceType.COLLABORATOR, ResourceType.CONTRACT],
            ActionType.UPDATE_ALL: [
                ResourceType.COLLABORATOR,
                ResourceType.CONTRACT,
                ResourceType.EVENT,
            ],
            ActionType.DELETE: [ResourceType.COLLABORATOR],
        },
        RoleType.SALES: {
            ActionType.CREATE: [ResourceType.CLIENT, ResourceType.EVENT],
            ActionType.UPDATE_MINE: [ResourceType.CLIENT, ResourceType.CONTRACT],
        },
        RoleType.SUPPORT: {
            ActionType.UPDATE_MINE: [ResourceType.EVENT],
        },
    }

    @staticmethod
    def has_permission(role, action, resource):
        base_permissions = deepcopy(PermissionManager.BASE_PERMISSIONS)
        try:
            role_permissions = PermissionManager.PERMISSIONS[role]
        except KeyError:
            raise KeyError(f"Role {role} not found")
        for permission in role_permissions:
            base_permissions[permission].extend(role_permissions[permission])
        return resource in base_permissions.get(action, [])


class FilterPermissionManager:
    FILTER_PERMISSIONS = {
        RoleType.MANAGEMENT: {
            ResourceType.CONTRACT: {
                "status": ["signed", "pending", "cancelled"],
                "remaining_amount": [True],
            },
            ResourceType.EVENT: {
                "assign": ["all", "no-contact"],
            },
        },
        RoleType.SALES: {
            ResourceType.CONTRACT: {
                "assigned": [True],
                "status": ["signed", "pending", "cancelled"],
                "remaining_amount": [True],
            },
            ResourceType.CLIENT: {
                "assigned": [True],
            },
        },
        RoleType.SUPPORT: {
            ResourceType.EVENT: {
                "assign": ["all", "assigned"],
            }
        },
    }

    @staticmethod
    def can_use_filter(role, resource, filter_name, filter_value):
        """Checks if a role can use a specific filter
        with a given value on a specific resource."""
        role_perms = FilterPermissionManager.FILTER_PERMISSIONS.get(role, {})
        resource_perms = role_perms.get(resource, {})
        allowed_values = resource_perms.get(filter_name)

        # Value none means no filter by default
        if filter_value is None:
            return True

        if allowed_values is None:
            if isinstance(filter_value, bool) and filter_value is False:
                return True
            return False

        if isinstance(filter_value, bool):
            if filter_value is True:
                return True in allowed_values
            else:
                return True

        is_allowed = filter_value in allowed_values
        return is_allowed


def check_filters(resource, *filter_names):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                token = util.get_token()
                role = RoleType(token["role"])
            except Exception as e:
                view.display_error(f"Authentication error: {e}")
                return None

            for name in filter_names:
                if name in kwargs:
                    value = kwargs[name]
                    if not FilterPermissionManager.can_use_filter(
                        role, resource, name, value
                    ):
                        view.display_error(
                            f"Role '{role.value}' does not have permission to use filter "
                            f"'--{name}' with value '{value}' for resource '{resource.name}'."
                        )
                        return None
            return func(*args, **kwargs)

        return wrapper

    return decorator


def login_required(pass_token=False):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                token = util.get_token()
                if pass_token:
                    return func(*args, token=token, **kwargs)
                else:
                    return func(*args, **kwargs)
            except Exception as e:
                view.display_error(str(e))
                return

        return wrapper

    return decorator


def permission(*actions, resource):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                token = util.get_token()
                for action in actions:
                    if PermissionManager.has_permission(
                        RoleType(token["role"]), action, resource
                    ):
                        return func(*args, **kwargs)
                actions_str = " or ".join(action.name for action in actions)
                sentry_sdk.capture_exception(
                    PermissionError(
                        f"You do not have permission to perform "
                        f"{actions_str} on {resource.name}."
                    )
                )
                raise PermissionError(
                    f"You do not have permission to perform "
                    f"{actions_str} on {resource.name}."
                )

            except Exception as e:
                view.display_error(str(e))

        return wrapper

    return decorator

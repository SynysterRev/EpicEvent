import enum
import functools

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
        ActionType.READ: [ResourceType.EVENT, ResourceType.CONTRACT,
                          ResourceType.CLIENT, ResourceType.COLLABORATOR],
        ActionType.CREATE: [],
        ActionType.UPDATE_ALL: [],
        ActionType.UPDATE_MINE: [],
        ActionType.DELETE: []
    }

    PERMISSIONS = {
        RoleType.MANAGEMENT: {
            ActionType.CREATE: [ResourceType.COLLABORATOR, ResourceType.CONTRACT],
            ActionType.UPDATE_ALL: [ResourceType.COLLABORATOR, ResourceType.CONTRACT,
                                    ResourceType.EVENT],
            ActionType.DELETE: [ResourceType.COLLABORATOR]
        },
        RoleType.SALES: {
            ActionType.CREATE: [ResourceType.CONTRACT, ResourceType.EVENT],
            ActionType.UPDATE_MINE: [ResourceType.CLIENT, ResourceType.CONTRACT],
        },
        RoleType.SUPPORT: {
            ActionType.UPDATE_MINE: [ResourceType.EVENT],
        }
    }

    @staticmethod
    def has_permission(role, action, resource):
        base_permissions = PermissionManager.BASE_PERMISSIONS

        try:
            role_permissions = PermissionManager.PERMISSIONS[role]
        except KeyError:
            raise KeyError(f"Role {role} not found")
        for permission in role_permissions:
            base_permissions[permission].extend(role_permissions[permission])
        return resource in base_permissions.get(action, [])


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


def permission(action, resource):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                token = util.get_token()
                if PermissionManager.has_permission(RoleType(token["role"]), action,
                                                    resource):
                    return func(*args, **kwargs)
                else:
                    view.display_error(
                        f"You do not have permission to perform {action.name} on"
                        f" {resource.name}.")
                    return
            except Exception as e:
                view.display_error(str(e))

        return wrapper

    return decorator

import enum


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
            ActionType.READ: [ResourceType.CLIENT, ResourceType.CONTRACT],
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

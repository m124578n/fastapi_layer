from enum import Enum


class UserPermission(str, Enum):
    ADMIN = "admin"
    ATHLETE = "athlete"
    COACH = "coach"


class TrainType(str, Enum):
    TRAP_SHOOT = "trap_shoot"
    SKEET_SHOOT = "skeet_shoot"


class ContestStatus(str, Enum):
    INIT = "init"
    STOPPED = "stopped"
    RUNNING = "running"
    RESTART = "restart"
    FINISHED = "finished"
    CANCEL = "cancel"


normal_permissions = [UserPermission.ATHLETE, UserPermission.COACH]
high_permissions = [UserPermission.ADMIN, UserPermission.COACH]
top_permissions = [UserPermission.ADMIN]
all_permissions = [UserPermission.ADMIN, UserPermission.ATHLETE, UserPermission.COACH]

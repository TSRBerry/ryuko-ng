import json
import os.path
import os


def get_persistent_roles_path(bot):
    return os.path.join(bot.state_dir, "data/persistent_roles.json")


def get_persistent_roles(bot) -> dict[str, list[str]]:
    if os.path.isfile(get_persistent_roles_path(bot)):
        with open(get_persistent_roles_path(bot), "r") as f:
            return json.load(f)
    return {}


def set_persistent_roles(bot, contents: dict[str, list[str]]):
    with open(get_persistent_roles_path(bot), "w") as f:
        json.dump(contents, f)


def add_user_roles(bot, uid: int, roles: list[int]):
    uid = str(uid)
    roles = [str(x) for x in roles]

    persistent_roles = get_persistent_roles(bot)
    persistent_roles[uid] = roles
    set_persistent_roles(bot, persistent_roles)


def get_user_roles(bot, uid: int) -> list[str]:
    uid = str(uid)
    with open(get_persistent_roles_path(bot), "r") as f:
        roles = json.load(f)
        if uid in roles:
            return roles[uid]
        return []

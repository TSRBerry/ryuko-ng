import json
import os

from robocop_ng.helpers.data_loader import read_json


def get_disabled_paths_path(bot) -> str:
    return os.path.join(bot.state_dir, "data/disabled_paths.json")


def get_disabled_paths(bot) -> list[str]:
    disabled_paths = read_json(bot, get_disabled_paths_path(bot))
    if "paths" not in disabled_paths.keys():
        return []
    return disabled_paths["paths"]


def set_disabled_paths(bot, contents: list[str]):
    with open(get_disabled_paths_path(bot), "w") as f:
        json.dump({"paths": contents}, f)


def is_path_disabled(bot, path: str) -> bool:
    for disabled_path in get_disabled_paths(bot):
        if disabled_path in path.strip().lower():
            return True
    return False


def add_disabled_path(bot, disabled_path: str) -> bool:
    disabled_path = disabled_path.strip().lower()
    disabled_paths = get_disabled_paths(bot)
    if disabled_path not in disabled_paths:
        disabled_paths.append(disabled_path)
        set_disabled_paths(bot, disabled_paths)
        return True
    return False


def remove_disabled_path(bot, disabled_path: str) -> bool:
    disabled_path = disabled_path.strip().lower()
    disabled_paths = get_disabled_paths(bot)
    if disabled_path in disabled_paths:
        disabled_paths.remove(disabled_path)
        set_disabled_paths(bot, disabled_paths)
        return True
    return False

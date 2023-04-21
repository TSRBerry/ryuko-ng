import json
import os


def get_disabled_tids_path(bot) -> str:
    return os.path.join(bot.state_dir, "data/disabled_tids.json")


def is_tid_valid(tid: str) -> bool:
    return len(tid) == 16 and tid.isalnum()


def get_disabled_tids(bot) -> dict[str, str]:
    if os.path.isfile(get_disabled_tids_path(bot)):
        with open(get_disabled_tids_path(bot), "r") as f:
            return json.load(f)
    return {}


def set_disabled_tids(bot, contents: dict[str, str]):
    with open(get_disabled_tids_path(bot), "w") as f:
        json.dump(contents, f)


def is_tid_disabled(bot, tid: str) -> bool:
    disabled_tids = get_disabled_tids(bot)
    tid = tid.lower()
    return tid in disabled_tids.keys()


def add_disabled_tid(bot, tid: str, note="") -> bool:
    disabled_tids = get_disabled_tids(bot)
    tid = tid.lower()
    if tid not in disabled_tids.keys():
        disabled_tids[tid] = note
        set_disabled_tids(bot, disabled_tids)
        return True
    return False


def remove_disabled_tid(bot, tid: str) -> bool:
    disabled_tids = get_disabled_tids(bot)
    tid = tid.lower()
    if tid in disabled_tids.keys():
        del disabled_tids[tid]
        set_disabled_tids(bot, disabled_tids)
        return True
    return False

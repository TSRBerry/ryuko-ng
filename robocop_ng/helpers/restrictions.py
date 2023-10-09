import json
import os

from robocop_ng.helpers.notifications import report_critical_error


def get_restrictions_path(bot):
    return os.path.join(bot.state_dir, "data/restrictions.json")


def get_restrictions(bot):
    if os.path.isfile(get_restrictions_path(bot)):
        with open(get_restrictions_path(bot), "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError as e:
                content = f.read()
                report_critical_error(
                    bot,
                    e,
                    additional_info={
                        "file": {"length": len(content), "content": content}
                    },
                )
    return {}


def set_restrictions(bot, contents):
    with open(get_restrictions_path(bot), "w") as f:
        f.write(contents)


def get_user_restrictions(bot, uid):
    uid = str(uid)
    rsts = get_restrictions(bot)
    if uid in rsts:
        return rsts[uid]
    return []


def add_restriction(bot, uid, rst):
    # mostly from kurisu source, credits go to ihaveamac
    uid = str(uid)
    rsts = get_restrictions(bot)
    if uid not in rsts:
        rsts[uid] = []
    if rst not in rsts[uid]:
        rsts[uid].append(rst)
    set_restrictions(bot, json.dumps(rsts))


def remove_restriction(bot, uid, rst):
    # mostly from kurisu source, credits go to ihaveamac
    uid = str(uid)
    rsts = get_restrictions(bot)
    if uid not in rsts:
        rsts[uid] = []
    if rst in rsts[uid]:
        rsts[uid].remove(rst)
    set_restrictions(bot, json.dumps(rsts))

import json
import math
import os

from robocop_ng.helpers.notifications import report_critical_error


def get_crontab_path(bot):
    return os.path.join(bot.state_dir, "data/robocronptab.json")


def get_crontab(bot):
    if os.path.isfile(get_crontab_path(bot)):
        with open(get_crontab_path(bot), "r") as f:
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


def set_crontab(bot, contents):
    with open(get_crontab_path(bot), "w") as f:
        f.write(contents)


def add_job(bot, job_type, job_name, job_details, timestamp):
    timestamp = str(math.floor(timestamp))
    job_name = str(job_name)
    ctab = get_crontab(bot)

    if job_type not in ctab:
        ctab[job_type] = {}

    if timestamp not in ctab[job_type]:
        ctab[job_type][timestamp] = {}

    ctab[job_type][timestamp][job_name] = job_details
    set_crontab(bot, json.dumps(ctab))


def delete_job(bot, timestamp, job_type, job_name):
    timestamp = str(timestamp)
    job_name = str(job_name)
    ctab = get_crontab(bot)

    del ctab[job_type][timestamp][job_name]

    set_crontab(bot, json.dumps(ctab))

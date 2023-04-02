import json
import os
from typing import Optional, Union

MACROS_FILE = "data/macros.json"


def get_macros_dict() -> dict[str, dict[str, Union[list[str], str]]]:
    if os.path.isfile(MACROS_FILE):
        with open(MACROS_FILE, "r") as f:
            macros = json.load(f)

        # Migration code
        if "aliases" not in macros.keys():
            new_macros = {"macros": macros, "aliases": {}}
            unique_macros = set(new_macros["macros"].values())
            for macro_text in unique_macros:
                first_macro_key = ""
                duplicate_num = 0
                for key, macro in new_macros["macros"].copy().items():
                    if macro == macro_text and duplicate_num == 0:
                        first_macro_key = key
                        duplicate_num += 1
                        continue
                    elif macro == macro_text:
                        if first_macro_key not in new_macros["aliases"].keys():
                            new_macros["aliases"][first_macro_key] = []
                        new_macros["aliases"][first_macro_key].append(key)
                        del new_macros["macros"][key]
                        duplicate_num += 1

            set_macros(new_macros)
            return new_macros

        return macros
    return {"macros": {}, "aliases": {}}


def is_macro_key_available(
    key: str, macros: dict[str, dict[str, Union[list[str], str]]] = None
) -> bool:
    if macros is None:
        macros = get_macros_dict()
    if key in macros["macros"].keys():
        return False
    for aliases in macros["aliases"].values():
        if key in aliases:
            return False
    return True


def set_macros(contents: dict[str, dict[str, Union[list[str], str]]]):
    with open(MACROS_FILE, "w") as f:
        json.dump(contents, f)


def get_macro(key: str) -> Optional[str]:
    macros = get_macros_dict()
    key = key.lower()
    if key in macros["macros"].keys():
        return macros["macros"][key]
    for main_key, aliases in macros["aliases"].items():
        if key in aliases:
            return macros["macros"][main_key]
    return None


def add_macro(key: str, message: str) -> bool:
    macros = get_macros_dict()
    key = key.lower()
    if is_macro_key_available(key, macros):
        macros["macros"][key] = message
        set_macros(macros)
        return True
    return False


def add_aliases(key: str, aliases: list[str]) -> bool:
    macros = get_macros_dict()
    key = key.lower()
    success = False
    if key in macros["macros"].keys():
        for alias in aliases:
            alias = alias.lower()
            if is_macro_key_available(alias, macros):
                macros["aliases"][key].append(alias)
                success = True
        if success:
            set_macros(macros)
    return success


def edit_macro(key: str, message: str) -> bool:
    macros = get_macros_dict()
    key = key.lower()
    if key in macros["macros"].keys():
        macros["macros"][key] = message
        set_macros(macros)
        return True
    return False


def remove_aliases(key: str, aliases: list[str]) -> bool:
    macros = get_macros_dict()
    key = key.lower()
    success = False
    if key not in macros["aliases"].keys():
        return False
    for alias in aliases:
        alias = alias.lower()
        if alias in macros["aliases"][key]:
            macros["aliases"][key].remove(alias)
            if len(macros["aliases"][key]) == 0:
                del macros["aliases"][key]
            success = True
    if success:
        set_macros(macros)
    return success


def remove_macro(key: str) -> bool:
    macros = get_macros_dict()
    key = key.lower()
    if key in macros["macros"].keys():
        del macros["macros"][key]
        set_macros(macros)
        return True
    return False


def clear_aliases(key: str) -> bool:
    macros = get_macros_dict()
    key = key.lower()
    if key in macros["macros"].keys() and key in macros["aliases"].keys():
        del macros["aliases"][key]
        set_macros(macros)
        return True
    return False

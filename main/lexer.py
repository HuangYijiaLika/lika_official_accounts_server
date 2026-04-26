"""
本文件是“命令解析器”（lexer）。
把用户发来的文本（如 help / commit / query / group-commit）解析成结构化 dict，供 views/services 调用。
"""

import re


def match_optional_text(pattern: str, command: str) -> str | None:
    match = re.search(pattern, command)
    if match:
        return match.group(1)
    return None


def match_optional_int(pattern: str, command: str) -> int | None:
    match = re.search(pattern, command)
    if match:
        return int(match.group(1))
    return None


def has_flag(pattern: str, command: str) -> bool:
    return re.search(pattern, command) is not None


def parse_command(command: str) -> dict | None:
    command = command.strip()
    if not command:
        return None

    edit_match = re.fullmatch(r"edit\s+(\S+)(.*)", command)
    if edit_match:
        public_id = edit_match.group(1)
        rest = edit_match.group(2).strip()
        if not rest:
            return None

        if rest.startswith("--"):
            parts = rest.split()
            if len(parts) % 2 != 0:
                return None
            updates: dict = {}
            allowed = {
                "--company": ("company", str),
                "--city": ("city", str),
                "--position": ("position", str),
                "--salary": ("salary", int),
            }
            for i in range(0, len(parts), 2):
                key = parts[i]
                value = parts[i + 1]
                if key not in allowed:
                    return None
                field_name, cast = allowed[key]
                try:
                    updates[field_name] = cast(value)
                except Exception:
                    return None
            if not updates:
                return None
            return {"command": "edit_update", "id": public_id, "updates": updates}

        replace_match = re.fullmatch(r"(\S+)\s+(\S+)\s+(\S+)\s+(\d+)", rest)
        if not replace_match:
            return None
        company, city, position, salary = replace_match.groups()
        return {
            "command": "edit_replace",
            "id": public_id,
            "company": company,
            "city": city,
            "position": position,
            "salary": int(salary),
        }

    if re.fullmatch(r"delete\s+--all", command):
        return {"command": "delete_all"}

    delete_match = re.fullmatch(r"delete\s+(\S+)", command)
    if delete_match:
        return {"command": "delete_one", "id": delete_match.group(1)}

    if re.fullmatch(r"help", command):
        return {"command": "help"}

    commit_match = re.fullmatch(r"commit\s+(\S+)\s+(\S+)\s+(\S+)\s+(\d+)", command)
    if commit_match:
        company, city, position, salary = commit_match.groups()
        return {
            "command": "commit",
            "company": company,
            "city": city,
            "position": position,
            "salary": int(salary),
        }

    if re.match(r"query\b", command):
        return {
            "command": "query",
            "id": match_optional_text(r"(?:--id)\s+(\S+)", command),
            "company": match_optional_text(r"(?:--company|-co)\s+(\S+)", command),
            "city": match_optional_text(r"(?:--city|-ci)\s+(\S+)", command),
            "position": match_optional_text(r"(?:--position|-po)\s+(\S+)", command),
            "page": match_optional_int(r"(?:--page|-pa)\s+(\d+)", command),
            "sort-new": has_flag(r"--sort-new\b", command),
            "sort-salary": has_flag(r"--sort-salary\b", command),
        }

    group_match = re.fullmatch(r"group-commit((?:\s+\S+)+)", command)
    if group_match:
        raw_items = group_match.group(1).split()
        if len(raw_items) % 4 != 0:
            return None

        offers = []
        for index in range(0, len(raw_items), 4):
            offers.append(
                {
                    "company": raw_items[index],
                    "city": raw_items[index + 1],
                    "position": raw_items[index + 2],
                    "salary": int(raw_items[index + 3]),
                }
            )
        return {"command": "group-commit", "offers": offers}

    return None

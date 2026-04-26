"""
本文件是“命令解析器”（lexer）。
把用户发来的文本（如 help / commit / query / group-commit）解析成结构化 dict，供 views/services 调用。
"""

import re


def match_optional_text(pattern: str, command: str) -> str | None:
    """在 command 中用正则 pattern 搜索可选文本参数，返回捕获组 1 或 None。"""
    match = re.search(pattern, command)
    if match:
        return match.group(1)
    return None


def match_optional_int(pattern: str, command: str) -> int | None:
    """在 command 中用正则 pattern 搜索可选整数参数，返回 int 或 None。"""
    match = re.search(pattern, command)
    if match:
        return int(match.group(1))
    return None


def has_flag(pattern: str, command: str) -> bool:
    """判断 command 中是否存在匹配 pattern 的标志位。"""
    return re.search(pattern, command) is not None


def parse_command(command: str) -> dict | None:
    """把用户输入命令解析为 tokens dict；解析失败返回 None。"""
    command = command.strip()
    if not command:
        return None

    # edit 有两种形态：
    # 1) edit <id> --field value [--field value...]
    # 2) edit <id> <company> <city> <position> <salary>
    edit_match = re.fullmatch(r"edit\s+(\S+)(.*)", command)
    if edit_match:
        public_id = edit_match.group(1)
        rest = edit_match.group(2).strip()
        if not rest:
            return None

        if rest.startswith("--"):
            # update 形态：参数必须成对出现，且字段名只能在白名单内
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

        # replace 形态：必须恰好 4 个字段，且 salary 为整数
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

    # delete <id>
    delete_match = re.fullmatch(r"delete\s+(\S+)", command)
    if delete_match:
        return {"command": "delete_one", "id": delete_match.group(1)}

    if re.fullmatch(r"ping", command):
        return {"command": "ping"}

    if re.fullmatch(r"stats", command):
        return {"command": "stats"}

    my_match = re.fullmatch(r"my(?:\s+--page\s+(\d+))?", command)
    if my_match:
        page = int(my_match.group(1)) if my_match.group(1) is not None else None
        return {"command": "my", "page": page}

    latest_match = re.fullmatch(r"latest(?:\s+(\d+))?", command)
    if latest_match:
        n = int(latest_match.group(1)) if latest_match.group(1) is not None else None
        return {"command": "latest", "n": n}

    help_one_match = re.fullmatch(r"help\s+(\S+)", command)
    if help_one_match:
        return {"command": "help_one", "target": help_one_match.group(1)}

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

    detail_match = re.fullmatch(r"detail\s+(\S+)", command)
    if detail_match:
        return {"command": "detail", "id": detail_match.group(1)}

    # query 支持多种可选参数（--company / --city / --position / --page / sort flags）
    if re.match(r"query\b", command):
        if has_flag(r"(?:--id)\b", command):
            return None
        return {
            "command": "query",
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

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

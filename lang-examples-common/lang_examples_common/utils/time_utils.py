def get_readable_duration(delta) -> str:

    if delta.total_seconds() < 0:
        return ""

    msg = []
    comp_name_map = {"hours": "h", "minutes": "m", "seconds": "s"}
    for comp_name in ["hours", "minutes", "seconds"]:
        comp = getattr(delta.components, comp_name)
        if comp:
            msg.append(f"{comp}{comp_name_map[comp_name]}")
    return " ".join(msg)


def get_secs_from_readable_duration(duration: str) -> int:
    """
    Convert a string like "1h 30m 10s" to seconds
    """
    secs = 0
    for part in duration.split():
        if part.endswith("h"):
            secs += int(part[:-1]) * 3600
        elif part.endswith("m"):
            secs += int(part[:-1]) * 60
        elif part.endswith("s"):
            secs += int(part[:-1])
    return secs

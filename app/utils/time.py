def duration_to_seconds(duration: str) -> int:
    if not duration:
        return 0
    if duration.endswith("s"):
        return int(duration[:-1])
    return 0
    
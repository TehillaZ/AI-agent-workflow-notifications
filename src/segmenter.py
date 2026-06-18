# SMS messages are limited to 160 characters per segment (GSM-7).
MAX_SEGMENT_CHARS = 160


def min_sms_segments(message):
    """Minimum number of SMS segments needed to deliver `message`
    without splitting any word across segments. Used to report how
    many billable SMS parts a notification will consume."""
    if not message or not message.strip():
        return 0
    words = message.split()
    if not words:
        return 0
    return _min_segments_from(words, 0)


def _min_segments_from(words, start):
    if start >= len(words):
        return 0
    best = None
    current_len = 0
    for end in range(start, len(words)):
        add = len(words[end]) if current_len == 0 else len(words[end]) + 1
        if current_len + add > MAX_SEGMENT_CHARS:
            break
        current_len += add
        rest = _min_segments_from(words, end + 1)
        candidate = rest + 1
        if best is None or candidate < best:
            best = candidate
    return best if best is not None else 0

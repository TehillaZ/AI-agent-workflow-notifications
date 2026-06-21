"""Phase 6: segmenter edge-case coverage."""

from segmenter import MAX_SEGMENT_CHARS, min_sms_segments


def test_empty_message_returns_zero():
    assert min_sms_segments("") == 0


def test_whitespace_only_returns_zero():
    assert min_sms_segments("   ") == 0


def test_short_message_returns_one_segment():
    assert min_sms_segments("hello world") == 1


def test_word_exactly_max_chars_fits_one_segment():
    word = "a" * MAX_SEGMENT_CHARS
    assert min_sms_segments(word) == 1


def test_word_longer_than_max_chars_returns_zero():
    word = "a" * (MAX_SEGMENT_CHARS + 1)
    assert min_sms_segments(word) == 0


def test_two_words_exceeding_max_chars_need_two_segments():
    word_a = "a" * 80
    word_b = "b" * 80
    message = f"{word_a} {word_b}"
    assert len(message) > MAX_SEGMENT_CHARS
    assert min_sms_segments(message) == 2

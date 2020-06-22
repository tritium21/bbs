# https://github.com/thomasballinger/curtsies/blob/master/curtsies/curtsieskeys.py
# https://github.com/jangler/readlike/blob/master/readlike.py

__all__ = ['edit', 'keys']


def _backward_char(text, pos):
    """Move pos back a character."""
    return text, max(0, pos - 1)


def _backward_delete_char(text, pos):
    """Delete the character behind pos."""
    if pos == 0:
        return text, pos
    return text[: pos - 1] + text[pos:], pos - 1


def _backward_kill_word(text, pos):
    """"
    Kill the word behind pos. Word boundaries are the same as those
    used by _backward_word.
    """
    text, new_pos = _backward_word(text, pos)
    return text[:new_pos] + text[pos:], new_pos


def _backward_word(text, pos):
    """
    Move pos back to the start of the current or previous word. Words
    are composed of alphanumeric characters (letters and digits).
    """
    while pos > 0 and not text[pos - 1].isalnum():
        pos -= 1
    while pos > 0 and text[pos - 1].isalnum():
        pos -= 1
    return text, pos


def _beginning_of_line(text, pos):
    """Move pos to the start of text."""
    return text, 0


def _capitalize_word(text, pos):
    """Capitalize the current (or following) word."""
    while pos < len(text) and not text[pos].isalnum():
        pos += 1
    if pos < len(text):
        text = text[:pos] + text[pos].upper() + text[pos + 1:]
    while pos < len(text) and text[pos].isalnum():
        pos += 1
    return text, pos


def _delete_char(text, pos):
    """Delete the character at pos."""
    return text[:pos] + text[pos + 1:], pos


def _delete_horizontal_space(text, pos):
    """Delete all spaces and tabs around pos."""
    while pos > 0 and text[pos - 1].isspace():
        pos -= 1
    end_pos = pos
    while end_pos < len(text) and text[end_pos].isspace():
        end_pos += 1
    return text[:pos] + text[end_pos:], pos


def _downcase_word(text, pos):
    """Lowercase the current (or following) word."""
    text, new_pos = _forward_word(text, pos)
    return text[:pos] + text[pos:new_pos].lower() + text[new_pos:], new_pos


def _end_of_line(text, pos):
    """Move pos to the end of text."""
    return text, len(text)


def _forward_char(text, pos):
    """Move pos forward a character."""
    return text, min(pos + 1, len(text))


def _forward_word(text, pos):
    """
    Move pos forward to the end of the next word. Words are composed of
    alphanumeric characters (letters and digits).
    """
    while pos < len(text) and not text[pos].isalnum():
        pos += 1
    while pos < len(text) and text[pos].isalnum():
        pos += 1
    return text, pos


def _kill_line(text, pos):
    """Kill from pos to the end of text."""
    return text[:pos], pos


def _kill_word(text, pos):
    """
    Kill from pos to the end of the current word, or if between words,
    to the end of the next word. Word boundaries are the same as those
    used by _forward_word.
    """
    text, end_pos = _forward_word(text, pos)
    return text[:pos] + text[end_pos:], pos


def _transpose_chars(text, pos):
    """
    Drag the character before pos forward over the character at pos,
    moving pos forward as well. If pos is at the end of text, then this
    transposes the two characters before pos.
    """
    if len(text) < 2 or pos == 0:
        return text, pos
    if pos == len(text):
        return text[:pos - 2] + text[pos - 1] + text[pos - 2], pos
    return text[:pos - 1] + text[pos] + text[pos - 1] + text[pos + 1:], pos + 1


def _transpose_words(text, pos):
    """
    Drag the word before pos past the word after pos, moving pos over
    that word as well. If pos is at the end of text, this transposes the
    last two words in text.
    """
    text, end2 = _forward_word(text, pos)
    text, start2 = _backward_word(text, end2)
    text, start1 = _backward_word(text, start2)
    text, end1 = _forward_word(text, start1)
    if start1 == start2:
        return text, pos
    return text[:start1] + text[start2:end2] + text[end1:start2:] + \
        text[start1:end1] + text[end2:], end2


def _unix_line_discard(text, pos):
    """Kill backward from pos to the beginning of text."""
    return text[pos:], 0


def _unix_word_rubout(text, pos):
    """
    Kill the word behind pos, using white space as a word boundary.
    """
    words = text[:pos].rsplit(None, 1)
    if len(words) < 2:
        return text[pos:], 0
    else:
        index = text.rfind(words[1], 0, pos)
        return text[:index] + text[pos:], index


def _upcase_word(text, pos):
    """Uppercase the current (or following) word."""
    text, new_pos = _forward_word(text, pos)
    return text[:pos] + text[pos:new_pos].upper() + text[new_pos:], new_pos

def _noop(text, pos):
    return text, pos

# TODO: Replace this with the actual key escapes
# TODO: https://github.com/urwid/urwid/blob/master/urwid/vterm.py
_key_bindings = {
    # TODO: C-I/tab (complete) - 0.2.0
    # TODO: C-N (next-history) - 0.2.0
    # TODO: C-P (previous-history) - 0.2.0
    # TODO: C-Y (yank) - 0.3.0
    # TODO: M-* (insert-completions) - 0.2.0
    # TODO: M-. (yank-last-arg) - 0.3.0
    # TODO: M-< eginning-of-history) - 0.2.0
    # TODO: M-> (end-of-history) - 0.2.0
    # TODO: M-C-I (tab-insert) - 0.2.0
    # TODO: M-C-Y (yank-nth-arg) - 0.3.0
    # TODO: M-C-[ (complete) - 0.2.0
    # TODO: M-Y (yank-pop) - 0.3.0
    # TODO: M-_ (yank-last-arg) - 0.3.0
    '\x7f': _backward_delete_char,
    '\x01': _beginning_of_line,
    '\x1b[H': _beginning_of_line,
    '\x02': _backward_char,
    '\x04': _delete_char,
    '\x05': _end_of_line,
    '\x1b[F': _end_of_line,
    '\x06': _forward_char,
    '\x08': _backward_delete_char,
    '\x0b': _kill_line,
    '\x1b\x08': _backward_kill_word,
    '\x14': _transpose_chars,
    '\x15': _unix_line_discard,
    '\x17': _unix_word_rubout,
    '\x1b[3~': _delete_char,
    '\x1b[4': _end_of_line,
    '\x1b[1': _beginning_of_line,
    '\x1b[D': _backward_char,
    '\x1b\\': _delete_horizontal_space,
    '\x1bb': _backward_word,
    '\x1b\x7f': _backward_kill_word,
    '\x1bc': _capitalize_word,
    '\x1bd': _kill_word,
    '\x1b\x1b[3~': _kill_word,
    '\x1bf': _forward_word,
    '\x1bl': _downcase_word,
    '\x1b\x1b[D': _backward_word,
    '\x1b\x1b[C': _forward_word,
    '\x1bt': _transpose_words,
    '\x1bu': _upcase_word,
    '\x1b[C': _forward_char,

}

_unhandeled = [
    '\x1b[A', # up
    '\x1b[B', # down
    '\x1b[5~', # pgup
    '\x1b[6~',  # pgdn
    '\x1b[5;2~',  # shift+pgup
    '\x1b[6;2~',  # shift+pgdn
    '\x1b[2~',  # ins
    '\x1b[1;2H',  # shift+home
    '\x1b[1;2F', # shift+end
]
KEYS = [
    "\x1b ",
    "\t",
    "\x1b[Z",
    "\x1b[A",
    "\x1b[B",
    "\x1b[C",
    "\x1b[D",
    "\x1bOA",
    "\x1bOB",
    "\x1bOC",
    "\x1bOD",
    "\x1b[1;5A",
    "\x1b[1;5B",
    "\x1b[1;5C",
    "\x1b[1;5D",
    "\x1b[5A",
    "\x1b[5B",
    "\x1b[5C",
    "\x1b[5D",
    "\x1b[1;9A",
    "\x1b[1;9B",
    "\x1b[1;9C",
    "\x1b[1;9D",
    "\x1b[1;10A",
    "\x1b[1;10B",
    "\x1b[1;10C",
    "\x1b[1;10D",
    "\x1bOP",
    "\x1bOQ",
    "\x1bOR",
    "\x1bOS",
    "\x1b[11~",
    "\x1b[12~",
    "\x1b[13~",
    "\x1b[14~",
    "\x1b[15~",
    "\x1b[17~",
    "\x1b[18~",
    "\x1b[19~",
    "\x1b[20~",
    "\x1b[21~",
    "\x1b[23~",
    "\x1b[24~",
    "\x00",
    "\x1c",
    "\x1d",
    "\x1e",
    "\x1f",
    "\x7f",
    "\x1b\x7f",
    "\xff",
    "\x1b\x1b[A",
    "\x1b\x1b[B",
    "\x1b\x1b[C",
    "\x1b\x1b[D",
    "\x1b",
    "\x1b[1~",
    "\x1b[4~",
    "\x1b\x1b[5~",
    "\x1b\x1b[6~",
    "\x1b[H",
    "\x1b[F",
    "\x1bOH",
    "\x1bOF",
    "\x1b[2~",
    "\x1b[3~",
    "\x1b[3;5~",
    "\x1b[5~",
    "\x1b[6~",
    "\x1b[7~",
    "\x1b[8~",
    "\x1b[OA",
    "\x1b[OB",
    "\x1b[OC",
    "\x1b[OD",
    "\x1b[OF",
    "\x1b[OH",
    "\x1b[[A",
    "\x1b[[B",
    "\x1b[[C",
    "\x1b[[D",
    "\x1b[[E",
]

def edit(text, pos, key):
    """
    Process a key input in the context of a line, and return the
    resulting text and cursor position.

    `text' and `key' must be of type str or unicode, and `pos' must be
    an int in the range [0, len(text)].

    If `key' is in keys(), the corresponding command is executed on the
    line. Otherwise, if `key' is a single character, that character is
    inserted at the cursor position. If neither condition is met, `text'
    and `pos' are returned unmodified.
    """
    if key in _key_bindings:
        return _key_bindings[key](text, pos)
    elif len(key) == 1:
        return text[:pos] + key + text[pos:], pos + 1
    else:
        return text, pos


def keys():
    """
    Return a frozenset of strings that describe key inputs corresponding
    to line editing commands.
    """
    return frozenset(KEYS)

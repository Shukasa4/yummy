import contextlib
import colored
import termios
import select
import tty
import sys
import re
import os


COLOR_NAMES = {
    'pink': 176,
    'red': 9,
    'purple': 69,
    'blue_green': 43,
    'light_orange': 173,
    'light_green': 151,
    'dark_green': 65,
    'dark_purple': 60,
}

ANSI_SPECIAL_KEY = '\x1b'
ANSI_COMMANDS = {
    'hide_cursor': "\x1b[?25l",
    'show_cursor': "\x1b[?25h",
    'get_cursor_position': "\x1b[6n",
    'clear_lines': '\x1b[1A\r\033[K',
}

KEYS = {
    '\r': 'enter',
    '\x1b\x5b\x41': 'arrow_up',
    '\x1b\x5b\x42': 'arrow_down',
}


def _execute_ansi_command(command_name, *args):
    sys.stdout.write(ANSI_COMMANDS[command_name].format(*args))


def colorize(text, color=251, attrib=None):
    if color in COLOR_NAMES:
        color = COLOR_NAMES[color]

    style = colored.fg(color)
    if attrib is not None:
        style += colored.attr(attrib)
    return colored.stylize(text, style, colored.attr('reset'))


def clear_lines(num_of_lines):
    for line in range(num_of_lines):
        _execute_ansi_command('clear_lines')


def get_terminal_size():
    rows, columns = os.popen('stty size', 'r').read().split()
    return int(rows), int(columns)


def clear_text(text):
    _, terminal_columns = get_terminal_size()
    stripped_ansi_text = strip_ansi(text)
    text_lines = stripped_ansi_text.expandtabs().split('\n')
    lines_to_clear = len(text_lines) - 1
    for line in text_lines:
        lines_to_clear += len(line) / terminal_columns
    clear_lines(lines_to_clear)


def get_cursor_position():
    _execute_ansi_command('get_cursor_position')
    ansi_result = ""
    while not ansi_result.endswith("R"):
        ansi_result += getch()
    pos_y, pos_x = re.findall(r"^\x1b\[(\d*);(\d*)R", ansi_result)[0]
    return int(pos_x), int(pos_y)


def strip_ansi(text):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    stripped_text = ansi_escape.sub('', text)
    return stripped_text


def hide_cursor():
    _execute_ansi_command('hide_cursor')


def show_cursor():
    _execute_ansi_command('show_cursor')


@contextlib.contextmanager
def hidden_cursor():
    try:
        hide_cursor()
        yield
    finally:
        show_cursor()


def get_keypress():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        user_key = sys.stdin.read(1)
        if user_key == ANSI_SPECIAL_KEY:
            user_key += sys.stdin.read(2)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    if user_key in KEYS:
        user_key = KEYS[user_key]
    return user_key

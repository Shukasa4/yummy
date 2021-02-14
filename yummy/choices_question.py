# -*- coding: utf-8 -*-
import textwrap
import colored

from yummy import terminal


def _indent_paragraph(text, color):
    paragraph_indent = terminal.colorize(' │ ', color)
    paragraph = ''
    for line in text.split('\n'):
        if terminal.strip_ansi(line) != '':
            paragraph +=  paragraph_indent + line + '\n'
        else:
            paragraph += line
    return paragraph


def _build_paragraph(question, choices, current_choice):
    paragraph_text = terminal.colorize(question, 'red')
    _, terminal_width = terminal.get_terminal_size()

    for choice_number, choice in enumerate(choices):
        wrapped_choice = textwrap.wrap(choice, terminal_width - 15)
        is_current_choice = current_choice == choice_number
        color = "pink" if is_current_choice else "dark_purple"

        if is_current_choice:
            choice_text = ' → {}. {}\n'.format(choice_number + 1, wrapped_choice[0])
        else:
            choice_text = '   {}. {}\n'.format(choice_number + 1, wrapped_choice[0])
        choice_text = terminal.colorize(choice_text, color)

        for other_line in wrapped_choice[1:]:
            choice_text += terminal.colorize('      {}\n'.format(other_line), color)
        paragraph_text += choice_text
    question_paragraph = _indent_paragraph(paragraph_text, 'dark_purple')
    return question_paragraph


def _user_select_choice(choices, current_choice):
    new_choice = current_choice
    is_final = False
    while new_choice == current_choice:
        user_key = terminal.get_keypress()
        if user_key == 'arrow_up':
            new_choice = max(0, current_choice - 1)
        elif user_key == 'arrow_down':
            new_choice = min(len(choices) - 1, current_choice + 1)
        elif user_key == 'enter':
            is_final = True
            break
    return new_choice, is_final


def choices_question(tw, question, choices):
    user_key = None
    current_choice = 0

    tw.write('\n\n')
    question_text = '• {}\n'.format(question)

    user_choice = None
    with terminal.hidden_cursor():
        while True:
            question_paragraph = _build_paragraph(question_text, choices, current_choice)
            tw.write(question_paragraph)

            current_choice, is_final = _user_select_choice(choices, current_choice)
            if is_final:
                break
            terminal.clear_text(question_paragraph)

    tw.write('\n')
    return choices[current_choice]

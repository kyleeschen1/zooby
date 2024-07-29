import os
import subprocess
import curses

import command
import save
from state import State
from logic import Or, And


def quit_loop(s):
    s.continue_running = False


def nl(screen, number=1):
    for i in range(number):
        screen.addstr("\n")


def print_title(menu, screen):
    screen.addstr(menu.border)
    nl(screen)
    screen.addstr(menu.title)
    nl(screen)
    screen.addstr(menu.border)
    nl(screen)


def print_cmd_map(menu, screen):
    for k, v in menu.cmd_map.items():
        if isinstance(v, list):
            doc = v[0]
            if isinstance(doc, str):
                nl(screen)
                screen.addstr("[" + k + "]  " + doc)


def print_menu(s):

    menu = s
    screen = s.screen

    screen.clear()
    print_title(menu, screen)
    nl(screen)
    screen.addstr(menu.description)
    nl(screen)
    print_cmd_map(menu, screen)


def run_search(s):

    s.set_description("Select directory in ~/Desktop with your files.")
    s.set_cmd_map({})
    print_menu(s)
    nl(s.screen)
    s.screen.refresh()

    directory_ls = subprocess.Popen(
        ["ls", s.path], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    fzf_cmd = subprocess.Popen(
        ["fzf", "--height", "40%", "--layout", "reverse"],
        stdin=directory_ls.stdout,
        stdout=subprocess.PIPE,
        encoding="utf-8",
    )

    curses.curs_set(0)
    o, e = fzf_cmd.communicate()

    s.directory = o.rstrip()
    s.path = s.path + "/" + s.directory

    directory_msg = "Directory: " + s.directory
    cmd_msg = "Now choose a search type."
    msg = directory_msg + "\n" + cmd_msg

    s.set_description(msg)
    s.set_cmd_map(
        {
            "a": ["And", build_search, False],
            "o": ["Or", build_search, True],
            "q": ["Quit", quit_loop],
        }
    )
    print_menu(s)
    curses.curs_set(0)


def execute_search(s):

    s.set_description("Running....")
    s.set_cmd_map({})
    print_menu(s)
    s.screen.refresh()

    pdf_search_cmd = subprocess.Popen(
        ["./shell/search_pdfs.sh", s.path, s.query.regex],
        stdout=subprocess.PIPE,
        encoding="utf-8",
    )

    o, e = pdf_search_cmd.communicate()

    results = []
    for line in o.splitlines():
        cols = line.split(":")
        text = ":".join(cols[2:])
        s.query.gather_results(cols, text, results)

    s.results = results
    n_results = len(s.results)

    save.save(s.filepath, s.result_column_names, s.results)

    s.set_description("Completed, with " + str(n_results) + " results!")
    s.set_cmd_map({"o": ["Open results", open_results], "q": ["Quit", quit_loop]})
    print_menu(s)


def open_results(s):

    open_results_process = subprocess.Popen(
        ["open", s.filepath],
        stdout=subprocess.PIPE,
        encoding="utf-8",
    )


def get_user_input(s, row, max_input_size=200):

    curses.nocbreak()
    curses.echo()
    curses.curs_set(1)

    user_input = s.screen.getstr(row, 0, max_input_size).decode("utf-8")

    curses.cbreak()
    curses.noecho()
    curses.curs_set(0)

    return user_input


def build_search(s, or_search):

    s.set_description("Enter words separated by spaces.")
    s.set_cmd_map({})
    print_menu(s)
    s.screen.refresh()

    search_terms = get_user_input(s, 6)

    if or_search:
        s.query = Or(search_terms)
    else:
        s.query = And(search_terms)

    s.search_terms = search_terms
    directory_msg = "Directory: " + s.directory
    search_term_msg = "Search terms: " + search_terms

    msg = directory_msg + "\n" + search_term_msg

    s.set_description(msg)
    s.set_cmd_map(
        {
            "r": ["Run", execute_search],
            "q": ["Quit", quit_loop],
        }
    )
    print_menu(s)


def run_event_loop(s):
    s.continue_running = True
    print_menu(s)
    while s.continue_running:
        key = s.screen.getkey()
        command.run(s, key)
        s.screen.refresh()


def initialize_state(screen):

    s = State(screen)

    # Display configuration
    s.border = "-------------------------------------------"

    # File configuration
    s.path = os.path.expanduser("~/Desktop")
    s.result_file_name = "results.tsv"
    s.filepath = s.path + "/" + s.result_file_name
    s.result_column_names = ["File", "Page", "Text"]

    # Set initial menu
    s.set_title("Zooby")
    s.set_description("Welcome to Zooby, the pdf search tool!")
    s.set_cmd_map(
        {
            "s": ["Set search directory", run_search],
            "q": ["Quit", quit_loop],
        }
    )
    return s


def main(screen):

    # Initialize screen
    screen.clear()
    curses.curs_set(0)

    # Initialize and configure program state
    s = initialize_state(screen)

    # Run the event loop
    run_event_loop(s)


if __name__ == "__main__":
    curses.wrapper(main)

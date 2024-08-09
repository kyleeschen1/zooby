import os
import subprocess
import curses

import command
import save
from state import State
from query import Or, And, Exact, postprocess_pdfgrep


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


def run_fzf_directory_selection(s):
    fzf_cmd = subprocess.Popen(
        f"(cd {s.desktop_path} && find . -type d -maxdepth 1 | sed '1d' | cut -c 3- | fzf --height 40% --layout reverse)",
        shell=True,
        stdout=subprocess.PIPE,
        encoding="utf-8",
    )
    return fzf_cmd.communicate()


def menu_set_directory(s):

    s.set_description("Select the folder with your files.")
    s.set_cmd_map()
    print_menu(s)
    nl(s.screen)
    s.screen.refresh()

    while True:
        o, e = run_fzf_directory_selection(s)
        if o != "":
            break

    # Set directory and file data
    s.directory = o.lstrip().rstrip()
    s.directory_path = s.desktop_path + "/" + s.directory
    s.filepath = s.directory_path + "/" + s.result_file_name

    menu_build_query(s)


def menu_build_query(s):

    # Prepare message
    directory_msg = "Folder: " + s.directory
    cmd_msg = "Now choose a search type."
    msg = directory_msg + "\n" + "\n" + cmd_msg

    s.set_description(msg)
    s.set_cmd_map(
        {
            "a": ["And", build_search, And],
            "o": ["Or", build_search, Or],
            "e": ["Exact", build_search, Exact],
            "q": ["Quit", quit_loop],
        }
    )
    curses.curs_set(0)
    print_menu(s)


def execute_search(s):

    s.set_description("Running...")
    s.set_cmd_map()
    print_menu(s)
    s.screen.refresh()

    pdf_search_cmd = subprocess.Popen(
        f" (cd {s.directory_path} && pdfgrep {s.query.regex} -n -i *pdf) ",
        shell=True,
        stdout=subprocess.PIPE,
        encoding="utf-8",
    )

    o, e = pdf_search_cmd.communicate()

    s.results = postprocess_pdfgrep(o, s.query)

    save.save(s.filepath, s.result_column_names, s.results)
    menu_show_results(s)


def menu_show_results(s):
    n_results = len(s.results)
    s.set_description(
        "Completed, with "
        + str(n_results)
        + " matches!"
        + "\n"
        + "Results have been saved to "
        + s.filepath
        + "."
    )
    s.set_cmd_map(
        {
            "o": ["Open results", open_results],
            "r": ["Rerun with new query", menu_build_query],
            "q": ["Quit", quit_loop],
        }
    )
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


def build_search(s, query_obj):

    s.set_description("Enter words separated by spaces.")
    s.set_cmd_map()
    print_menu(s)
    s.screen.refresh()

    # Get search terms from user, then build query object.
    s.search_terms = get_user_input(s, 6)
    s.query = query_obj(s.search_terms)

    # Build message
    directory_msg = "Folder: " + s.directory
    search_term_msg = "Query: " + s.search_terms
    msg = directory_msg + "\n" + search_term_msg + "\n\n" + "Choose your future!"

    s.set_description(msg)
    s.set_cmd_map(
        {
            "r": ["Run Query", execute_search],
            "e": ["Edit Query", menu_build_query],
            "f": ["Edit Folder", menu_set_directory],
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
    s.desktop_path = os.path.expanduser("~/Desktop").rstrip()
    s.result_file_name = "results.tsv"
    s.result_column_names = ["File", "Page", "Text"]

    # Set initial menu
    s.set_title("Zooby")
    s.set_description(
        "Welcome to Zooby, the pdf search tool!"
        + "\n"
        + "\n"
        + "Please put the pdfs in a folder on your desktop before proceeding."
    )
    s.set_cmd_map(
        {
            "s": ["Set search directory", menu_set_directory],
            "q": ["Quit", quit_loop],
        }
    )
    return s


def launch_cli(screen):

    # Initialize screen
    screen.clear()
    curses.curs_set(0)

    # Initialize and configure program state
    s = initialize_state(screen)

    # Run the event loop
    run_event_loop(s)


def main():
    curses.wrapper(launch_cli)


if __name__ == "__main__":
    main()

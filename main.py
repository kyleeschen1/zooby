import os
import subprocess
import curses


def do_nothing(state):
    pass


def dispatch_on_key(key, cmd_map):
    "Returns the cmd specified by the key."
    try:
        return cmd_map[key]
    except KeyError:
        return do_nothing


def apply_cmd(state, cmd):
    "Applies a command to state, along with args if specified."
    if isinstance(cmd, list):
        first = cmd[0]
        if isinstance(first, str):
            op, args = cmd[1], cmd[2:]
        else:
            op, args = first, cmd[1:]
        if args:
            op(state, *args)
        else:
            op(state)
    else:
        cmd(state)


class Env:

    def __init__(self):
        self.locals = {}

    def bind(self, key, value):
        self.locals[key] = value

    def resolve(self, key):
        return self.locals[key]


class State:

    def __init__(self, screen):
        self.screen = screen
        self.continue_running = True
        self.env = Env()
        self.border = "-------------------------------------------"

    def set_title(self, title):
        self.title = title

    def set_description(self, description):
        self.description = description

    def set_cmd_map(self, cmd_map):
        self.cmd_map = cmd_map

    def run(self):
        cmd = dispatch_on_key(self.key, self.cmd_map)
        apply_cmd(self, cmd)


def clear(state):
    state.screen.clear()


def display_output(state):
    # state.screen.addstr(state.key)
    pass


def quit_loop(state):
    state.continue_running = False


def list_fn(state, args):
    print(args)


def print_cmds(state):
    for k, v in state.cmd_map.items():
        print(k + str(v))


def run_shell(shell_cmd):
    output = subprocess.run(shell_cmd, capture_output=True)
    return output.stdout.decode("utf-8")


def shell(state, shell_cmd):
    output = subprocess.run(shell_cmd, capture_output=True)
    output = output.stdout.decode("utf-8")
    state.output = output
    state.screen.addstr(output)


def nl(s, number=1):
    for i in range(number):
        s.addstr("\n")


def print_title(menu, s):
    s.addstr(menu.border)
    nl(s)
    s.addstr(menu.title)
    nl(s)
    s.addstr(menu.border)
    nl(s)


def print_cmd_map(menu, s):
    for k, v in menu.cmd_map.items():
        if isinstance(v, list):
            doc = v[0]
            if isinstance(doc, str):
                nl(s)
                s.addstr("[" + k + "]  " + doc)


def print_menu(state):

    menu = state
    s = state.screen

    s.clear()
    print_title(menu, s)
    nl(s)
    s.addstr(menu.description)
    nl(s)
    print_cmd_map(menu, s)


cmd_map_all = {
    "default": display_output,
    "c": clear,
    "d": ["List", list_fn, 1, 2, 3],
    "s": ["Shell", shell, "pwd"],
    "p": print_cmds,
    "r": ["Print Menu", print_menu],
    "q": ["Quit", quit_loop],
}


def run_search(state):

    state.set_description("Select directory in ~/Desktop with your files.")
    state.set_cmd_map({})
    print_menu(state)
    nl(state.screen)
    state.screen.refresh()

    path = os.path.expanduser("~/Desktop")
    directory_ls = subprocess.Popen(
        ["ls", path], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    head_cmd = subprocess.Popen(
        ["fzf", "--height", "40%", "--layout", "reverse"],
        stdin=directory_ls.stdout,
        stdout=subprocess.PIPE,
        encoding="utf-8",
    )

    curses.curs_set(0)
    o, e = head_cmd.communicate()

    state.directory = o.rstrip()
    state.path = path + "/" + state.directory

    directory_msg = "Directory: " + state.directory
    cmd_msg = "Now choose a search type."
    msg = directory_msg + "\n" + cmd_msg

    state.set_description(msg)
    state.set_cmd_map(
        {
            "a": ["And", build_search, True],
            "o": ["Or", build_search, False],
            "q": ["Quit", quit_loop],
        }
    )
    print_menu(state)
    curses.curs_set(0)


def build_regex(state):
    term_list = state.search_terms.split()
    return "|".join(term_list)


def execute_search(state):
    query = build_regex(state)

    state.set_description("Running....")
    state.set_cmd_map({})
    print_menu(state)
    state.screen.refresh()

    pdf_search_cmd = subprocess.Popen(
        ["zooby.sh", state.path, query],
        stdout=subprocess.PIPE,
        encoding="utf-8",
    )

    o, e = pdf_search_cmd.communicate()
    state.results = []
    for line in o.splitlines():
        cols = line.split(":")
        cols = [cols[0], cols[1], ":".join(cols[2:])]
        state.results.append(cols)
    n_results = len(state.results)

    import csv

    filepath = state.path + "/" + "results.tsv"
    open(filepath, "w").close()
    with open(filepath, "w", newline="") as csv_writer:
        writer = csv.writer(csv_writer, delimiter="\t")
        writer.writerow(["File", "Page", "Text"])
        writer.writerows(state.results)

    state.set_description("Completed, with " + str(n_results) + " results!")
    state.set_cmd_map({"o": ["Open results", open_results], "q": ["Quit", quit_loop]})
    print_menu(state)


def open_results(state):

    open_results_process = subprocess.Popen(
        ["open", state.path + "/results.tsv"],
        stdout=subprocess.PIPE,
        encoding="utf-8",
    )


def get_user_input(state, row, max_input_size=200):

    curses.nocbreak()
    curses.echo()
    curses.curs_set(1)

    user_input = state.screen.getstr(row, 0, max_input_size).decode("utf-8")

    curses.cbreak()
    curses.noecho()
    curses.curs_set(0)

    return user_input


def build_search(state, or_search):

    state.or_search = or_search
    state.set_description("Enter words separated by spaces.")
    state.set_cmd_map({})
    print_menu(state)
    state.screen.refresh()

    search_terms = get_user_input(state, 6)
    state.search_terms = search_terms
    directory_msg = "Directory: " + state.directory
    search_term_msg = "Search terms: " + search_terms

    msg = directory_msg + "\n" + search_term_msg

    state.set_description(msg)
    state.set_cmd_map(
        {
            "r": ["Run", execute_search],
            "q": ["Quit", quit_loop],
        }
    )
    print_menu(state)


def run_event_loop(state):
    print_menu(state)
    while state.continue_running:
        state.key = state.screen.getkey()
        state.run()
        state.screen.refresh()


def main(screen):

    # Initialize screen
    screen.clear()
    curses.curs_set(0)

    # Initialize program state
    state = State(screen)
    state.set_title("Zooby")
    state.set_description("Welcome to Zooby, the legal search tool!")
    state.set_cmd_map(
        {
            "default": display_output,
            "s": ["Set search directory", run_search],
            "q": ["Quit", quit_loop],
        }
    )

    # Run the event loop
    run_event_loop(state)


if __name__ == "__main__":
    curses.wrapper(main)

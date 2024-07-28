import os
import subprocess
import curses


# output = Subprocess.run(["echo", "Geeks for geeks"], capture_output=True)
# print("Hello" + output.stdout.decode("utf-8"))


def dispatch_on_key(key, cmd_map):
    "Returns the cmd specified by the key."
    try:
        return cmd_map[key]
    except KeyError:
        return cmd_map["default"]


def apply_cmd(state, cmd):
    "Applies a command to state, along with args if specified."
    if isinstance(cmd, list):
        op, args = cmd[0], cmd[1:]
        op(state, args)
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

    def __init__(self, screen, cmd_map):
        self.screen = screen
        self.cmd_map = cmd_map
        self.continue_running = True
        self.env = Env()

    def run(self):
        cmd = dispatch_on_key(self.key, self.cmd_map)
        apply_cmd(self, cmd)


def clear(state):
    state.screen.clear()


def display_output(state):
    print(state.key)


def quit_loop(state):
    state.continue_running = False


def list_fn(state, args):
    print(args)


def shell(state, shell_cmd):
    output = subprocess.run(shell_cmd, capture_output=True)
    output = output.stdout.decode("utf-8")
    state.output = output
    print(output)


cmd_map_init = {
    "default": display_output,
    "q": quit_loop,
    "c": clear,
    "d": [list_fn, 1, 2, 3],
    "s": [shell, "pwd"],
}


def run_event_loop(state):
    while state.continue_running:
        state.key = state.screen.getkey()
        state.run()
        state.screen.refresh()


def main(screen):

    # Initialize state and screen
    screen.clear()
    state = State(screen, cmd_map_init)

    # Run the event loop
    run_event_loop(state)


if __name__ == "__main__":
    curses.wrapper(main)

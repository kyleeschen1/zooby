import os
import subprocess
import curses


# output = subprocess.run(["echo", "Geeks for geeks"], capture_output=True)
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


class State:

    def __init__(self, screen, cmd_map):
        self.screen = screen
        self.cmd_map = cmd_map
        self.continue_running = True

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


cmd_map_init = {
    "default": display_output,
    "q": quit_loop,
    "c": clear,
    "d": [list_fn, 1, 2, 3],
}


def main(screen):

    screen.clear()
    state = State(screen, cmd_map_init)

    while state.continue_running:
        state.key = screen.getkey()
        state.run()
        screen.refresh()


if __name__ == "__main__":
    curses.wrapper(main)

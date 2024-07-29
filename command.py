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


def do_nothing(state):
    pass


def dispatch_on_key(key, cmd_map):
    "Returns the cmd specified by the key."
    try:
        return cmd_map[key]
    except KeyError:
        return do_nothing


def run(state, key):
    cmd = dispatch_on_key(key, state.cmd_map)
    apply_cmd(state, cmd)

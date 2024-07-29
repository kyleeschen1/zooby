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
        self.env = Env()

    def set_title(self, title):
        self.title = title

    def set_description(self, description):
        self.description = description

    def set_cmd_map(self, cmd_map):
        self.cmd_map = cmd_map

class Or:

    def __init__(self, query):
        self.query = query
        term_list = query.split()
        self.regex = "|".join(term_list)

    def gather_results(self, cols, text, results):
        results.append([cols[0], cols[1], text])


class And:

    def __init__(self, query):
        term_list = query.split()
        self.query = query
        self.regex = term_list[0]
        self.check_terms = term_list[1:]

    def gather_results(self, cols, text, results):
        if all(t in text for t in self.check_terms):
            results.append([cols[0], cols[1], text])

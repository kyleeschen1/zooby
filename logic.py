class Or:

    def __init__(self, query):
        self.query = query
        term_list = query.split()
        self.regex = "|".join(term_list)

    def post_pdfgrep_check(self, text):
        return True


class And:

    def __init__(self, query):
        term_list = query.split()
        self.query = query
        self.regex = term_list[0]
        self.check_terms = term_list[1:]

    def post_pdfgrep_check(self, text):
        return all(t in text for t in self.check_terms)

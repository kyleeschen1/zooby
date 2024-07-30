class Exact:

    def __init__(self, query):
        self.query = query
        self.regex = '"' + query + '"'

    def post_pdfgrep_check(self, text):
        return True


class Or:

    def __init__(self, query):
        self.query = query
        term_list = query.split()
        self.regex = "\|".join(term_list)

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


def postprocess_pdfgrep(pdfgrep_output, query):

    results = []

    for line in pdfgrep_output.splitlines():

        # pdfgrep uses ":" to delimit columns
        cols = line.split(":")

        # adjusts for accidental splitting of the text column
        text = ":".join(cols[2:])

        # "And" queries need to check whether the all words
        # but the first also appear in the narrowed search space.
        if query.post_pdfgrep_check(text):
            row = [cols[0], cols[1], text]
            results.append(row)

    return results

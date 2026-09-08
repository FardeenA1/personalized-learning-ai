class DNAGenerator:

    def __init__(self, profile):

        self.profile = profile
    def writing_complexity(self):

        length = self.profile["avg_sentence_length"]

        if length <= 10:

            return "Very Simple"

        elif length <= 15:

            return "Simple"

        elif length <= 22:

            return "Moderate"

        else:

            return "Complex"
    def paragraph_style(self):

        avg = self.profile["avg_paragraph_length"]

        if avg < 2:

            return "Very Short"

        elif avg < 4:

            return "Medium"

        else:

            return "Long"
    def formatting(self):

        return {

            "bullets":

            self.profile["uses_bullets"],

            "numbering":

            self.profile["uses_numbering"],

            "headings":

            self.profile["headings"]

        }
    def vocabulary(self):

        words = [

            word

            for word, count

            in self.profile["common_words"]

        ]

        return words[:20]
    def learning_flow(self):

        flow = []

        headings = [

            h.lower()

            for h in self.profile["headings"]

        ]

        keywords = [

            "definition",

            "meaning",

            "example",

            "advantages",

            "summary",

            "conclusion"

        ]

        for word in keywords:

            for heading in headings:

                if word in heading:

                    flow.append(word)

                    break

        return flow
    def generate(self):

        return {

            "writing_style":{

                "complexity":

                self.writing_complexity(),

                "paragraph_style":

                self.paragraph_style()

            },

            "formatting":

            self.formatting(),

            "learning_flow":

            self.learning_flow(),

            "favorite_words":

            self.vocabulary()

        }
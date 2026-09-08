import re


class PatternAnalyzer:

    def __init__(self, text):

        self.lines = [
            line.strip()
            for line in text.split("\n")
            if line.strip()
        ]
    def detect_sections(self):

         patterns = []

         keywords = [

            "definition",
            "meaning",
            "introduction",

            "example",

            "advantages",
            "disadvantages",

            "importance",

            "summary",

            "conclusion",

            "formula",

            "diagram",

            "note",

            "remember"
            ]

         for line in self.lines:

            lower = line.lower()

            for keyword in keywords:

                if keyword in lower:

                    patterns.append(keyword)

                    break

         return patterns
    def writing_flow(self):

        flow = self.detect_sections()

        return " → ".join(flow)
    def pattern_frequency(self):
        counter = {}
        for item in self.detect_sections():
            counter[item] = counter.get(item, 0) + 1

        return counter
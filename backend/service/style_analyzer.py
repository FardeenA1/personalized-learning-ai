import re
from collections import Counter

import spacy

nlp = spacy.load("en_core_web_sm")


class StyleAnalyzer:

    def __init__(self, text):
        self.text = text
        self.doc = nlp(text)

    def get_sentences(self):
        return list(self.doc.sents)

    def get_paragraphs(self):
        paragraphs = [
            p.strip()
            for p in self.text.split("\n\n")
            if p.strip()
        ]
        return paragraphs

    def average_sentence_length(self):
        sentences = self.get_sentences()
        if not sentences:
            return 0
        total_words = sum(
            len(sentence.text.split())
            for sentence in sentences
        )
        return round(total_words / len(sentences), 2)

    def average_paragraph_length(self):
        paragraphs = self.get_paragraphs()
        if not paragraphs:
            return 0
        total_sentences = 0
        for paragraph in paragraphs:
            total_sentences += len(list(nlp(paragraph).sents))
        return round(total_sentences / len(paragraphs), 2)

    def uses_bullets(self):
        bullet_pattern = r"^[\-\*\•]"
        lines = self.text.split("\n")
        bullet_lines = [
            line for line in lines
            if re.match(bullet_pattern, line.strip())
        ]
        return len(bullet_lines) > 3

    def uses_numbering(self):
        pattern = r"^\d+\."
        lines = self.text.split("\n")
        numbered = [
            line for line in lines
            if re.match(pattern, line.strip())
        ]
        return len(numbered) > 3

    def common_words(self, top_n=20):
        words = [
            token.text.lower()
            for token in self.doc
            if token.is_alpha
            and not token.is_stop
            and len(token.text) > 3]
        counter = Counter(words)
        return counter.most_common(top_n)

    def build_learning_dna(self):
        return {
            "avg_sentence_length": self.average_sentence_length(),
            "avg_paragraph_length": self.average_paragraph_length(),
            "uses_bullets": self.uses_bullets(),
            "uses_numbering": self.uses_numbering(),
        }


def normalize_subject(subject):
    if not subject:
        return ""
    return subject.strip().lower()
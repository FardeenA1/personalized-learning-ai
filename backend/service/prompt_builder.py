class PromptBuilder:

    def __init__(self, learning_dna, textbook_text, mode="normal", has_source=True):
        self.learning_dna = learning_dna
        self.textbook_text = textbook_text
        self.mode = mode
        self.has_source = has_source

    def build_style_prompt(self):
        style = self.learning_dna

        complexity = style["writing_style"]["complexity"]
        paragraph_style = style["writing_style"]["paragraph_style"]
        learning_flow = style["learning_flow"]
        favorite_words = style["favorite_words"]
        uses_bullets = style["formatting"]["bullets"]
        uses_numbering = style["formatting"]["numbering"]

        instructions = []

        instructions.append(
            f"Write at a '{complexity}' complexity level: "
            f"{'use short, direct sentences with simple vocabulary' if complexity in ['Very Simple', 'Simple'] else 'use detailed, nuanced sentences with richer vocabulary' if complexity == 'Complex' else 'balance sentence length and vocabulary, avoiding both oversimplification and overcomplication'}."
        )

        instructions.append(
            f"Structure paragraphs to be '{paragraph_style}': "
            f"{'keep each paragraph to 1-2 sentences' if paragraph_style == 'Very Short' else 'keep each paragraph to 3-4 sentences' if paragraph_style == 'Medium' else 'allow paragraphs of 5+ sentences when the topic needs depth'}."
        )

        if uses_bullets:
            instructions.append(
                "This student's notes rely heavily on bullet points. "
                "You MUST break down key ideas into bullet points wherever the content has multiple related facts, steps, or characteristics — do not just write plain paragraphs."
            )
        else:
            instructions.append(
                "This student rarely uses bullet points. Write mostly in flowing paragraph form."
            )

        if uses_numbering:
            instructions.append(
                "This student's notes use numbered lists for sequences or ordered concepts. "
                "You MUST use numbered lists (1., 2., 3.) for any sequential steps, ordered principles, or ranked points."
            )

        if learning_flow:
            instructions.append(
                f"Structure the explanation following this section order where relevant: {', '.join(learning_flow)}."
            )

        if favorite_words:
            instructions.append(
                f"If natural, you may occasionally use vocabulary similar to: {', '.join(favorite_words[:10])} — but never force these in if they don't fit."
            )

        return "\n".join(f"- {line}" for line in instructions)

    def build_exam_prompt(self):
        return (
            "\n\nAdditionally, add these sections at the end:\n"
            "- Important Points (bullet list of the most exam-critical facts)\n"
            "- Quick Revision (a condensed summary in 3-5 lines)\n"
            "- Expected Viva Questions (3-5 likely questions with 1-line answers)\n"
        )

    def build_rewrite_instructions(self):
        return (
            "\n\nCRITICAL RULES:\n"
            "- Preserve the exact same points, facts, and their original order — do not merge, reorder, add, or remove ideas.\n"
            "- This is a STYLE rewrite, not a summary or a re-explanation — keep the same level of detail as the source.\n"
            "- Only change sentence structure, formatting (bullets/numbering/paragraphs), and word choice to match the style rules above.\n"
            "- Do not add unrelated facts. Do not mention that you are an AI or that these are 'rewritten' notes — just produce the notes directly.\n"
        )

    def build_normal_prompt(self):
        return (
            "\n\nCRITICAL RULES:\n"
            "- Preserve the exact same points, facts, and their original order — do not merge, reorder, add, or remove ideas.\n"
            "- This is a STYLE rewrite, not a summary or a re-explanation — keep the same level of detail as the source.\n"
            "- Only change sentence structure, formatting (bullets/numbering/paragraphs), and word choice to match the style rules above.\n"
            "- Be concise. Do not pad with extra explanation, repetition, or filler sentences beyond what the source already says. Roughly match the length of the source content, do not expand it significantly.\n"
            "- Do not add unrelated facts. Do not mention that you are an AI or that these are 'rewritten' notes — just produce the notes directly.\n"
        )

    def build_generate_instructions(self):
        return (
            "\n\nCRITICAL RULES:\n"
            "- No source material was provided. Generate accurate, well-structured study notes on this topic from your own knowledge.\n"
            "- Cover the core concepts a student would need to understand this topic well — definitions, key points, and examples where relevant.\n"
            "- Keep it concise: aim for around 200-300 words total. Do not over-elaborate or repeat the same idea in different words.\n"
            "- Follow the style rules above strictly for formatting and tone.\n"
            "- Do not mention that you are an AI or that these are 'generated' notes — just produce the notes directly.\n"
        )

    def generate_prompt(self):
        prompt = "You are writing study notes to match a specific student's personal writing and formatting style.\n\n"
        prompt += "STYLE RULES (follow strictly):\n"
        prompt += self.build_style_prompt()

        if self.mode == "exam":
            prompt += self.build_exam_prompt()

        if self.has_source:
            prompt += self.build_rewrite_instructions()
            prompt += "\n\nSource content to rewrite:\n\n"
            prompt += self.textbook_text
        else:
            prompt += self.build_generate_instructions()
            prompt += f"\n\nTopic to write notes on:\n\n{self.textbook_text}"

        return prompt


def build_plain_prompt(topic, textbook_text, has_source):

    if has_source:
        return (
            "Rewrite the following content clearly and accurately, "
            "preserving all key points and their order. Be concise — "
            "roughly match the length of the source, don't pad it. "
            "Do not mention that you are an AI.\n\n"
            f"{textbook_text}"
        )

    return (
        "Write clear, accurate, well-structured study notes on this topic. "
        "Keep it concise, around 200-300 words. "
        "Do not mention that you are an AI.\n\n"
        f"Topic: {topic}"
    )
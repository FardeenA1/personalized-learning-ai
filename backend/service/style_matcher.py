from service.style_analyzer import StyleAnalyzer
from service.pattern_analyzer import PatternAnalyzer
from service.dna_generator import DNAGenerator


COMPLEXITY_LEVELS = ["Very Simple", "Simple", "Moderate", "Complex"]
PARAGRAPH_LEVELS = ["Very Short", "Medium", "Long"]


def _score_ordinal(original, generated, levels):
    if original not in levels or generated not in levels:
        return 0.5

    if original == generated:
        return 1.0

    distance = abs(levels.index(original) - levels.index(generated))
    max_distance = len(levels) - 1

    return max(0.0, 1.0 - (distance / max_distance))


def _score_boolean(original, generated):
    return 1.0 if original == generated else 0.0


def compute_style_match(original_dna, generated_text):

    analyzer = StyleAnalyzer(generated_text)
    pattern_analyzer = PatternAnalyzer(generated_text)

    features = analyzer.build_learning_dna()
    features["common_words"] = analyzer.common_words()
    features["headings"] = pattern_analyzer.detect_sections()

    generated_dna = DNAGenerator(features).generate()

    complexity_score = _score_ordinal(
        original_dna["writing_style"]["complexity"],
        generated_dna["writing_style"]["complexity"],
        COMPLEXITY_LEVELS
    )

    paragraph_score = _score_ordinal(
        original_dna["writing_style"]["paragraph_style"],
        generated_dna["writing_style"]["paragraph_style"],
        PARAGRAPH_LEVELS
    )

    bullets_score = _score_boolean(
        original_dna["formatting"]["bullets"],
        generated_dna["formatting"]["bullets"]
    )

    numbering_score = _score_boolean(
        original_dna["formatting"]["numbering"],
        generated_dna["formatting"]["numbering"]
    )

    overall = (complexity_score + paragraph_score + bullets_score + numbering_score) / 4

    return {
        "overall_match": round(overall * 100, 1),
        "breakdown": {
            "complexity": round(complexity_score * 100, 1),
            "paragraph_style": round(paragraph_score * 100, 1),
            "bullets": round(bullets_score * 100, 1),
            "numbering": round(numbering_score * 100, 1)
        }
    }
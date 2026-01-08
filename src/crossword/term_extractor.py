"""
Term extraction utilities for crossword puzzle generation.

This module provides functions to extract meaningful terms from source text
that are suitable for crossword puzzles.
"""

import re
from collections import Counter
from dataclasses import dataclass


# Common English words to exclude (stop words)
STOP_WORDS = {
    'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
    'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
    'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
    'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their', 'what',
    'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go', 'me',
    'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him', 'know', 'take',
    'people', 'into', 'year', 'your', 'good', 'some', 'could', 'them', 'see',
    'other', 'than', 'then', 'now', 'look', 'only', 'come', 'its', 'over',
    'think', 'also', 'back', 'after', 'use', 'two', 'how', 'our', 'work',
    'first', 'well', 'way', 'even', 'new', 'want', 'because', 'any', 'these',
    'give', 'day', 'most', 'us', 'is', 'are', 'was', 'were', 'been', 'being',
    'has', 'had', 'does', 'did', 'done', 'doing', 'such', 'here', 'where',
    'very', 'more', 'much', 'many', 'each', 'every', 'both', 'few', 'own',
    'same', 'through', 'during', 'before', 'between', 'under', 'again',
    'further', 'once', 'why', 'while', 'should', 'must', 'might', 'may'
}


@dataclass
class ExtractedTerm:
    """Represents a term extracted from source text."""
    term: str
    frequency: int
    context: str  # Sentence where term appears


def extract_terms_from_text(
    text: str,
    min_length: int = 4,
    max_length: int = 15,
    max_terms: int = 25,
    include_proper_nouns: bool = True
) -> list:
    """
    Extract meaningful terms from text for crossword puzzle generation.

    Args:
        text: Source text to extract terms from
        min_length: Minimum word length to consider
        max_length: Maximum word length to consider
        max_terms: Maximum number of terms to return
        include_proper_nouns: Whether to include capitalized words

    Returns:
        List of ExtractedTerm objects sorted by relevance
    """
    # Split into sentences for context
    sentences = re.split(r'[.!?]+', text)
    sentence_map = {}  # word -> first sentence containing it

    # Extract all words
    words = re.findall(r'\b[A-Za-z]+\b', text)

    # Count frequencies
    word_counts = Counter()

    for sentence in sentences:
        sentence_words = re.findall(r'\b[A-Za-z]+\b', sentence)
        for word in sentence_words:
            word_lower = word.lower()
            word_counts[word_lower] += 1

            # Store first sentence as context
            if word_lower not in sentence_map:
                sentence_map[word_lower] = sentence.strip()

    # Filter words
    filtered_terms = []

    for word, count in word_counts.items():
        # Check length constraints
        if len(word) < min_length or len(word) > max_length:
            continue

        # Skip stop words
        if word.lower() in STOP_WORDS:
            continue

        # Check if word only contains letters
        if not word.isalpha():
            continue

        context = sentence_map.get(word, "")
        filtered_terms.append(ExtractedTerm(
            term=word.upper(),
            frequency=count,
            context=context[:200]  # Truncate context
        ))

    # Sort by frequency (higher = more important)
    filtered_terms.sort(key=lambda x: x.frequency, reverse=True)

    # Return top terms
    return filtered_terms[:max_terms]


def extract_terms_from_code(code: str, language: str = "python") -> list:
    """
    Extract meaningful terms from source code.

    Focuses on:
    - Function and class names
    - Variable names (using naming conventions)
    - Comments and docstrings
    - String literals

    Args:
        code: Source code text
        language: Programming language (affects parsing)

    Returns:
        List of ExtractedTerm objects
    """
    terms = []

    if language.lower() == "python":
        # Extract function names
        functions = re.findall(r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', code)
        for func in functions:
            # Convert snake_case to words
            words = func.split('_')
            for word in words:
                if len(word) >= 4:
                    terms.append(ExtractedTerm(
                        term=word.upper(),
                        frequency=1,
                        context=f"Function: {func}"
                    ))

        # Extract class names
        classes = re.findall(r'class\s+([A-Z][a-zA-Z0-9]*)', code)
        for cls in classes:
            # Split CamelCase
            words = re.findall(r'[A-Z][a-z]+', cls)
            for word in words:
                if len(word) >= 4:
                    terms.append(ExtractedTerm(
                        term=word.upper(),
                        frequency=1,
                        context=f"Class: {cls}"
                    ))

        # Extract from docstrings
        docstrings = re.findall(r'"""(.*?)"""', code, re.DOTALL)
        docstrings += re.findall(r"'''(.*?)'''", code, re.DOTALL)
        for doc in docstrings:
            doc_terms = extract_terms_from_text(doc)
            terms.extend(doc_terms)

        # Extract from comments
        comments = re.findall(r'#\s*(.+)$', code, re.MULTILINE)
        for comment in comments:
            comment_terms = extract_terms_from_text(comment)
            terms.extend(comment_terms)

    # Deduplicate by term
    seen = set()
    unique_terms = []
    for term in terms:
        if term.term not in seen:
            seen.add(term.term)
            unique_terms.append(term)

    return unique_terms


def suggest_clue(term: str, context: str) -> str:
    """
    Generate a suggested clue based on term and context.

    This provides a starting point that should be refined by Claude
    for better educational value.

    Args:
        term: The word to create a clue for
        context: Sentence or phrase where the term appears

    Returns:
        A suggested clue string
    """
    # Simple template-based clue generation
    # Claude will generate better clues, but this provides a fallback

    if context:
        # Create fill-in-the-blank style clue
        if term.lower() in context.lower():
            blank_context = re.sub(
                rf'\b{re.escape(term)}\b',
                '_____',
                context,
                flags=re.IGNORECASE
            )
            if len(blank_context) < 100:
                return blank_context

    return f"[Define: {term}]"


if __name__ == "__main__":
    # Example usage
    sample_text = """
    Machine learning is a subset of artificial intelligence that enables
    computers to learn from data without being explicitly programmed.
    Neural networks are computational models inspired by biological neurons.
    Deep learning uses multiple layers of neural networks to process
    complex patterns. Training involves adjusting weights through backpropagation.
    """

    terms = extract_terms_from_text(sample_text)

    print("Extracted Terms:")
    print("-" * 50)
    for term in terms:
        print(f"{term.term}: appears {term.frequency} time(s)")
        print(f"  Context: {term.context[:80]}...")
        print()

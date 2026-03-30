"""
sentence_parser.py — Parse an input sentence and extract subject, verb, object,
and whether it is a question. Loops until 'quit' is entered.
"""

import spacy

nlp = spacy.load("en_core_web_sm")

QUESTION_WORDS = {"who", "what", "where", "when", "why", "how", "which", "whose", "whom"}


def is_question(text: str, doc) -> bool:
    text = text.strip()
    if text.endswith("?"):
        return True
    first = doc[0].text.lower() if doc else ""
    if first in QUESTION_WORDS:
        return True
    # auxiliary before subject (e.g. "Is the cat sleeping")
    if doc and doc[0].pos_ == "AUX":
        return True
    return False


def extract_svo(doc):
    subject = None
    verb = None
    obj = None

    for token in doc:
        if token.dep_ in ("nsubj", "nsubjpass") and subject is None:
            subject = token.text
        if token.pos_ in ("VERB", "AUX") and verb is None:
            verb = token.lemma_
        if token.dep_ in ("dobj", "pobj", "attr", "oprd") and obj is None:
            obj = token.text

    return subject, verb, obj


def main():
    print("Sentence parser - type 'quit' to exit.\n")

    while True:
        text = input("Enter input sentence: ").strip()
        if text.lower() in ("quit", "q", "exit"):
            print("Goodbye.")
            break
        if not text:
            continue

        doc = spacy.load("en_core_web_sm")(text) if False else nlp(text)

        subject, verb, obj = extract_svo(doc)
        question = is_question(text, doc)

        print(f"\n  Subject  : {subject or '-'}")
        print(f"  Verb     : {verb or '-'}")
        print(f"  Object   : {obj or '-'}")
        print(f"  Question : {'yes' if question else 'no'}\n")


if __name__ == "__main__":
    main()

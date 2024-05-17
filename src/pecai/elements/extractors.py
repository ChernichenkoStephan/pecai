import spacy

import typing

from . import entity


class SpacyExtractor:
    def __init__(self, processors, nlp=None):
        self._processors = processors
        self._nlp = nlp if nlp else spacy.load("ru_core_news_sm")
        self._doc = None

    def _extract(self, text: str) -> typing.Iterable[entity.Entity]:
        text = text.replace("\n", " ")
        self._doc = self._nlp(text)
        return [self._entity_from_span(span) for span in self._doc.ents]

    def _entity_from_span(self, ent: spacy.tokens.span.Span) -> entity.Entity:
        return entity.Entity(ent.lemma_, ent.start_char, ent.end_char, ent.label_)

    def extract(self, text: str) -> typing.Iterable[entity.Entity]:
        entities = self._extract(text)
        for p in self._processors:
            entities = p(entities)
        return entities

    def __call__(self, text: str) -> typing.Iterable[entity.Entity]:
        return self.extract(text)

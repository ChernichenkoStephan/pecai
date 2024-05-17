import pymystem3

import typing

from . import patterns
from . import links
from . import entity


class Disambiguator(links.BaseLink):
    def __init__(self, thesaurus: dict = dict(), lemmatizer=pymystem3.Mystem()):
        self.__lemmatizer = lemmatizer
        self.__thesaurus = thesaurus

    def disambiguate(self, entity: entity.Entity) -> entity.Entity:
        if entity.identity:
            entity.identity = self._disambiguate(entity.identity)
        return entity

    def _disambiguate(self, identity: str) -> str:
        identity = patterns.nonword_pattern.sub(r"", identity)
        if identity in self.__thesaurus:
            return identity
        identity = "".join(self.__lemmatizer.lemmatize(identity)[:-1])
        for core, synonims in self.__thesaurus.items():
            if identity in synonims:
                return core
        return identity

    def __call__(
        self, entities: typing.Iterable[entity.Entity]
    ) -> typing.Iterable[entity.Entity]:
        return [self.disambiguate(entity) for entity in entities]

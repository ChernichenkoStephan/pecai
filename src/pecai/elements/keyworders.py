import typing

from . import links
from . import entity


class Keyworder(links.BaseLink):
    def __call__(self, entities: typing.Iterable[entity.Entity]) -> list[str]:
        return list([ent.value for ent in entities])

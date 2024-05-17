from dataclasses import dataclass


@dataclass
class Entity:
    value: str
    start: int
    stop: int
    type_: str

    @property
    def identity(self) -> str | None:
        return self.value

    @identity.setter
    def identity(self, value: str):
        self.value = value

import random
from abc import ABC, abstractmethod

from .locations import Direction, Room, NoConnectingRoom
from .entity import Entity


class ApparentCharacter(Entity):
    def __init__(self, behavior, location: Room, unreal: bool = False):
        self.behavior = behavior
        super().__init__(location, unreal)

    def move(self, direction):
        self.location = self.location.get_neighbor(direction)

    def tick(self):
        self.behavior.tick(self)


class Behavior(ABC):
    @classmethod
    @abstractmethod
    def tick(cls, character: ApparentCharacter):
        raise NotImplementedError()


class MoveStraight(Behavior):
    @classmethod
    def tick(cls, character: ApparentCharacter):
        for direction in Direction:
            try:
                character.move(direction)
                return
            except NoConnectingRoom:
                pass


class Character(ApparentCharacter):
    _NAME_LIST = [
        "Noah",
        "Oliver",
        "George",
        "Arthur",
        "Muhammad",
        "Leo",
        "Harry",
        "Oscar",
        "Archie",
        "Henry",
        "Olivia",
        "Amelia",
        "Isla",
        "Ava",
        "Ivy",
        "Freya",
        "Lily",
        "Florence",
        "Mia",
        "Willow",
    ]

    def __init__(self, location: Room):
        self.name = random.choice(self._NAME_LIST)
        super().__init__(MoveStraight, location)

    def __str__(self):
        return self.name


class CharacterProjection(ApparentCharacter):
    def __init__(self, real: Character, expected_behavior: Behavior):
        super().__init__(expected_behavior, real.location, True)

        self.character = real

    def __str__(self):
        return f"Projection of {self.character.name}"

import random
from abc import ABC, abstractmethod

from .entity import Entity
from .locations import Direction, NoConnectingRoom, Room


class ApparentCharacter(Entity):
    def __init__(self, behavior, location: Room, unreal: bool = False):
        self.behavior = behavior
        super().__init__(location, unreal)

    def move(self, direction):
        new_location = self.location.get_neighbor(direction)
        self.logger.info(f"Moving {direction} to {new_location}")
        self.location = new_location

    def tick(self):
        self.behavior.tick(self)


class Behavior(ABC):
    @classmethod
    @abstractmethod
    def tick(cls, character: ApparentCharacter):
        raise NotImplementedError()

    @classmethod
    def to_json(cls):
        # Should probably add a description here
        return cls.__name__


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
    _all_characters = {}

    def __init__(self, location: Room):
        self.name = random.choice(self._NAME_LIST)
        super().__init__(MoveStraight, location)
        self._all_characters[self.id] = self

    @classmethod
    def get_character(cls, character_id):
        return cls._all_characters[character_id]

    @classmethod
    def get_all(cls):
        return cls._all_characters.values()

    def to_json(self, include_location=True, include_behaviour=False):
        description = {
            "id": self.id,
            "name": self.name,
        }
        if include_location:
            description["location"] = self.location.id
        if include_behaviour:
            description["behavior"] = self.behavior.to_json()

        return description

    def __str__(self):
        return self.name


class CharacterProjection(ApparentCharacter):
    def __init__(self, real: Character, expected_behavior: Behavior):
        super().__init__(expected_behavior, real.location, True)

        self.character = real

    def to_json(self):
        return {
            "id": self.id,
            "character": self.character.to_json(include_location=False),
            "behaviour_guess": self.behavior.to_json(),
        }

    def __str__(self):
        return f"Projection of {self.character.name}"

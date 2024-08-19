import enum
import logging
import uuid
import random

_LOGGER = logging.getLogger("Mapping")


class Direction(enum.Enum):
    North = enum.auto()
    South = enum.auto()
    East = enum.auto()
    West = enum.auto()

    def opposite(self):
        return {
            Direction.North: Direction.South,
            Direction.South: Direction.North,
            Direction.East: Direction.West,
            Direction.West: Direction.East,
        }[self]


class NoConnectingRoom(Exception):
    pass


class Room:
    def __init__(self):
        self.id = uuid.uuid4()
        self.entities_present = set()
        self.neighbors = {}

        self._logger = _LOGGER.getChild(str(self.id))
        self._logger.info(f"Created room")

    def add_neighbor(self, other, direction):
        if direction.opposite() not in other.neighbors:
            self.neighbors[direction] = other
            other.neighbors[direction.opposite()] = self
            self._logger.debug(f"{other} is {direction}")
            return True
        else:
            self._logger.debug(f"Rejecting neighbor: {other} already linked")
            return False

    def get_neighbor(self, direction):
        try:
            return self.neighbors[direction]
        except KeyError as ex:
            raise NoConnectingRoom() from ex

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return f"<Room {self.id}>"


class Map:
    def __init__(self, num_rooms):
        self.rooms = [Room() for _ in range(num_rooms)]

        for room in self.rooms:
            for direction in Direction:
                if direction not in room.neighbors:
                    for _ in range(3):
                        chosen_room = random.choice(self.rooms)
                        if (chosen_room != room) and room.add_neighbor(
                            chosen_room, direction
                        ):
                            break
                    else:
                        room._logger.info(
                            f"Giving up on link. Too many attempt to find unoccupied partner"
                        )

            if not room.neighbors:
                room._logger.warning("Room has no links")

    def get_random_room(self):
        return random.choice(self.rooms)

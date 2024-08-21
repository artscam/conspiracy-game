import enum
import logging
import random
import uuid

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
    _room_names = [
        "Attic",
        "Loft",
        "Spare room",
        "Bedroom",
        "Bathroom",
        "Balcony",
        "Nursery",
        "Study",
        "Utility room",
        "Panic room",
        "Conservatory",
        "Living room",
        "Dining room",
        "Kitchen",
        "Garage",
        "Mud room",
        "Basement",
        "Games room",
        "Wine cellar",
        "Lobby",
        "Landing",
        "Operating theatre",
        "Parlor",
        "Control room",
        "Fusion core",
        "Wardrobe",
        "Shed",
        "Porch",
        "Library",
        "Tree house",
        "Greenhouse",
        "Engineering",
        "Galley",
    ]

    def __init__(self):
        self.id = uuid.uuid4()
        self.entities_present = set()
        self.neighbors = {}

        try:
            random.shuffle(self._room_names)
            self.name = self._room_names.pop()
        except IndexError as ex:
            raise IndexError("Ran out of names for rooms") from ex

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

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "entities_present": [str(entity.id) for entity in self.entities_present],
            "neighbors": {
                direction.name: str(room.id)
                for direction, room in self.neighbors.items()
            },
        }

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return f"<Room {self.id}>"


class Map:
    def __init__(self, num_rooms):
        rooms = [Room() for _ in range(num_rooms)]

        for room in rooms:
            for direction in Direction:
                if direction not in room.neighbors:
                    for _ in range(3):
                        chosen_room = random.choice(rooms)
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

        self.rooms = {room.id: room for room in rooms}

    def __getitem__(self, location_id: str | uuid.UUID):
        if not isinstance(location_id, uuid.UUID):
            key = uuid.UUID(location_id)
        else:
            key = location_id
        return self.rooms[key]

    def get_random_room(self):
        return random.choice(list(self.rooms.values()))

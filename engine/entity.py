import logging
import uuid

from .locations import Room


class Entity:
    def __init__(self, location: Room, unreal: bool = False):
        self.id = uuid.uuid4()
        self._location = None
        self.unreal = unreal

        self.logger = logging.getLogger(type(self).__name__).getChild(str(self))
        self.location = location

    def __repr__(self):
        return f"<{type(self).__name__}: {self.id}>"

    @property
    def location(self) -> Room:
        return self._location

    @location.setter
    def location(self, value: Room):
        if not self.unreal:
            if self._location is not None:
                self.location.entities_present.remove(self)
                self.logger.info(f"Moved from {self.location} to {value}")
            else:
                self.logger.info(f"Spawned at {value}")

        self._location = value

        if not self.unreal:
            self.location.entities_present.add(self)

    def tick(self):
        # By default, do nothing
        pass

import logging

from conspiracy.engine.locations import Map
from conspiracy.engine.characters import Character
from conspiracy.engine.player import Player


class Game:
    _NUM_ROOMS = 10
    _NUM_CHARACTERS = 2

    def __init__(self):
        self.logger = logging.getLogger("Game")

        self.map = Map(self._NUM_ROOMS)

        self.characters = [
            Character(self.map.get_random_room()) for _ in range(self._NUM_CHARACTERS)
        ]
        self.player = Player(self.map.get_random_room())

        self.entities = self.characters + [self.player]

    def tick_once(self):
        self.logger.info("Start of tick")
        for entity in self.entities:
            entity.tick()

    def run(self, num_ticks):
        for _ in range(num_ticks):
            self.tick_once()


def main():
    logging.basicConfig(level=logging.DEBUG)

    game = Game()
    game.run(10)

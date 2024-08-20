import logging
import coloredlogs
import falcon

from conspiracy.engine.locations import Map
from conspiracy.engine.characters import Character
from conspiracy.engine.player import Player
import conspiracy.engine.api


class Game:
    _NUM_ROOMS = 10
    _NUM_CHARACTERS = 2

    def __init__(self):
        self.logger = logging.getLogger("Game")
        self.tick = 0

        self.map = Map(self._NUM_ROOMS)

        self.characters = [
            Character(self.map.get_random_room()) for _ in range(self._NUM_CHARACTERS)
        ]
        self.player = Player(self.map.get_random_room())

        self.entities = self.characters + [self.player]

    def tick_once(self):
        self.tick += 1
        self.logger.info(f"Start of tick {self.tick}")

        for entity in self.entities:
            entity.tick()

    def run(self, num_ticks):
        for _ in range(num_ticks):
            self.tick_once()


def main():
    coloredlogs.install(
        level="DEBUG", fmt="%(asctime)s,%(msecs)03d %(name)s %(levelname)s %(message)s"
    )

    game = Game()
    conspiracy.engine.api.run_webapp(game)

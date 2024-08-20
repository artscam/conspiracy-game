from collections import defaultdict


from conspiracy.engine import entity
from conspiracy.engine import locations
from conspiracy.engine import characters


class GuessAlreadyDisproven(Exception):
    pass


class AlreadyMoved(Exception):
    pass


class Player(entity.Entity):
    def __init__(self, start_pos: locations.Room):
        super().__init__(start_pos)
        self.remembered_projections = {}
        self.visible_characters = set()
        self.visible_entities = set()
        self.incorrect_guesses = defaultdict(list)

        self.moved_this_tick = False
        self.update_visibility()

    def __str__(self):
        # This class mostly supports multiple players, so perhaps this should be a
        # variable name, but that's beyond the scope of a simple prototype
        return "Player"

    def move(self, direction):
        if self.moved_this_tick:
            raise AlreadyMoved()
        else:
            self.location = self.location.get_neighbor(direction)
            self.moved_this_tick = True

    def tick(self):
        self.moved_this_tick = False
        self.update_visibility()
        self.evaluate_guesses()

    def update_visibility(self):
        self.visible_entities = {
            entity for entity in self.location.entities_present if entity is not self
        }
        self.visible_characters = set(
            entity
            for entity in self.visible_entities
            if isinstance(entity, characters.Character)
        )

    def evaluate_guesses(self):
        for entity in self.visible_characters:
            try:
                projection = self.remembered_projections[entity]
            except KeyError:
                # There's no existing guess, so nothing to do
                continue

            if projection.location != entity.location:
                self.logger.info(f"Discarding inaccurate projection for {entity}")
                self.incorrect_guesses[entity].append(projection.behavior)
                del self.remembered_projections[entity]

    def make_guess(self, character, behavior):
        if behavior not in self.incorrect_guesses[character]:
            self.remembered_projections[character] = characters.CharacterProjection(
                character, behavior
            )
        else:
            raise GuessAlreadyDisproven()

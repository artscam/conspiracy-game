from collections import defaultdict

from conspiracy.engine import characters, entity, locations


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

        self.all_known_rooms = set()
        self.all_known_characters = set()

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
            self.all_known_rooms.add(self.location)

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
        self.all_known_characters.update(
            character.id for character in self.visible_characters
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

    def try_expand_character(self, character_id):
        try:
            projection = self.remembered_projections[character_id]
            return projection.to_json()
        except KeyError:
            if character_id in self.all_known_characters:
                return {
                    "character": characters.Character.get_character(
                        character_id
                    ).to_json(include_location=False)
                }
            else:
                raise KeyError(
                    f"Character {character_id} has never been observed by the player"
                )

    def describe_known_characters(self):
        return [
            self.try_expand_character(character)
            for character in self.all_known_characters
        ]

    def make_guess(self, character, behavior):
        if behavior not in self.incorrect_guesses[character]:
            self.remembered_projections[character] = characters.CharacterProjection(
                character, behavior
            )
        else:
            raise GuessAlreadyDisproven()

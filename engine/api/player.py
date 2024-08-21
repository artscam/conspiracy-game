import logging

import falcon

from ..locations import Direction, NoConnectingRoom
from ..player import AlreadyMoved


class PlayerComponent:
    def __init__(self, player, game):
        self.player = player
        self.game = game


class Movement(PlayerComponent):
    def on_post(self, req, resp):
        request_payload = req.media
        specified_direction = Direction[request_payload["direction"].title()]
        logging.debug(f"Web API requested {self.player} move {specified_direction}")

        try:
            self.player.move(specified_direction)
        except NoConnectingRoom as ex:
            logging.exception("Requested impossible movement")
            raise falcon.HTTPBadRequest(title="Impossible movement") from ex
        except AlreadyMoved as ex:
            logging.exception("Tried to move without advancing tick")
            raise falcon.HTTPBadRequest(
                title="Player has already moved this tick"
            ) from ex

        resp.media = {"new_location": self.player.location.id}

        if request_payload.get("advance_tick", True):
            logging.debug("Automatically advancing tick after player movement")
            self.game.tick_once()

            resp.media["new_tick"] = self.game.tick

    def on_get_location(self, req, resp):
        resp.media = {"location": self.player.location.id}


class VisibleEntities(PlayerComponent):
    def on_get(self, req, resp):
        resp.media = {
            "entities": [entity.to_json() for entity in self.player.visible_entities],
            "characters": [
                entity.to_json() for entity in self.player.visible_characters
            ],
        }

    def on_get_all_known(self, req, resp):
        resp.media = self.player.describe_known_characters()

    def on_get_known(self, req, resp, character_id):
        try:
            resp.media = self.player.try_expand_character(character_id)
        except KeyError as ex:
            raise falcon.HTTPBadRequest(
                title="Character not known to player",
                description=f"Character {character_id} is not known to the player, having never been observed",
            ) from ex


class PlayerView:
    def __init__(self, game, player, app: falcon.App):
        self.player = player
        self.game = game
        movement_controller = Movement(player, game)
        entities_controller = VisibleEntities(player, game)

        app.add_route("/player/move", movement_controller)
        app.add_route("/player/location", movement_controller, suffix="location")
        app.add_route("/player/entities_in_sight", entities_controller)
        app.add_route(
            "/player/known_character/{character_id:uuid}",
            entities_controller,
            suffix="known",
        )
        app.add_route(
            "/player/known_character",
            entities_controller,
            suffix="all_known",
        )

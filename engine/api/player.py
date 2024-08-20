import falcon
from ..locations import Direction, NoConnectingRoom
from ..player import AlreadyMoved
import logging


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

        resp.media = {"new_location": str(self.player.location.id)}

        if request_payload.get("advance_tick", True):
            logging.debug("Automatically advancing tick after player movement")
            self.game.tick_once()

            resp.media["new_tick"] = self.game.tick


class VisibleEntities(PlayerComponent):
    def on_get(self, req, resp):
        resp.media = {
            "entities": [str(entity.id) for entity in self.player.visible_entities],
            "characters": [str(entity.id) for entity in self.player.visible_characters],
        }


class Player:
    def __init__(self, game, player, app: falcon.App):
        self.player = player
        self.game = game

        app.add_route("/player/move", Movement(player, game))
        app.add_route("/player/entities_in_sight", VisibleEntities(player, game))

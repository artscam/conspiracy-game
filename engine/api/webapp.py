import functools
import json
import logging
import uuid
from wsgiref.simple_server import make_server

import conspiracy.engine.api as game_api
import falcon
import falcon.inspect


class UUIDCompatibleEncoder(json.JSONEncoder):
    """
    uuid.UUID is not, by default, serialisable into JSON.
    This encoder fixes that
    """

    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            return str(obj)
        else:
            return super().default(obj)


def run_webapp(game):
    webapp = falcon.App()

    # Install the custom JSON encoder which can handle UUIDs
    json_handler = falcon.media.JSONHandler(
        dumps=functools.partial(json.dumps, cls=UUIDCompatibleEncoder)
    )
    extra_handlers = {"application/json": json_handler}
    webapp.resp_options.media_handlers.update(extra_handlers)

    # Set up the API endpoints
    game_representation = game_api.GameView(game, webapp)
    player_representation = game_api.PlayerView(game, game.player, webapp)
    map_representation = game_api.RoomView(game.map, webapp)
    characters_representation = game_api.CharacterView(webapp)

    # Start the webserver
    app_description = falcon.inspect.inspect_app(webapp)
    logging.debug(
        f"Web frontend configured: {app_description.to_string(name='conspiracy-engine')}"
    )
    with make_server("", 8080, webapp) as httpd:
        logging.info("Starting web frontend")
        httpd.serve_forever()

import falcon
import falcon.inspect
import logging
from wsgiref.simple_server import make_server

import conspiracy.engine.api as game_api


def run_webapp(game):
    webapp = falcon.App()
    game_representation = game_api.Game(game, webapp)
    player_representation = game_api.Player(game, game.player, webapp)

    app_description = falcon.inspect.inspect_app(webapp)
    logging.debug(
        f"Web frontend configured: {app_description.to_string(name='conspiracy-engine')}"
    )
    with make_server("", 8080, webapp) as httpd:
        logging.info("Starting web frontend")
        httpd.serve_forever()

import falcon


class Ticks:
    """Report which tick we're on, or advance the game by POST"""

    def __init__(self, game_instance):
        self.game_instance = game_instance

    def on_get(self, req, resp):
        resp.media = {"current_tick": self.game_instance.tick}

    def on_post(self, req, resp):
        self.game_instance.tick_once()
        resp.media = {"current_tick": self.game_instance.tick}


class GameView:
    def __init__(self, game, app: falcon.App):
        self.game_instance = game
        app.add_route("/game/tick", Ticks(self.game_instance))

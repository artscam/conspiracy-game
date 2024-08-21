import falcon

from ..characters import Character


class CharacterView:
    def __init__(self, app: falcon.App):
        app.add_route("/character/get/{character_id:uuid}", self)
        app.add_route("/character/all", self, suffix="list")

    def on_get(self, req, resp, character_id):
        try:
            resp.media = Character.get_character(character_id).to_json(
                include_location=True, include_behaviour=True
            )
        except KeyError as ex:
            raise falcon.HTTPBadRequest(title="Character does not exist") from ex

    def on_get_list(self, req, resp):
        resp.media = [
            character.to_json(include_location=True, include_behaviour=True)
            for character in Character.get_all()
        ]

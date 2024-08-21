import falcon

from ..locations import Map, Room


class RoomView:
    def __init__(self, map: Map, app: falcon.App):
        self.map = map
        app.add_route("/location/{location_id:uuid}", self)

    def on_get(self, req, resp, location_id):
        try:
            room = self.map[location_id]
        except KeyError as ex:
            raise falcon.HTTPBadRequest(
                title="No such location",
                description=f"Location ID {location_id} does not exist",
            ) from ex

        resp.media = room.to_json()

import pathlib
from powerrelay.controllers import RelayController

PROJECT_ROOT = pathlib.Path(__file__).parent

#
# Global routes setup
#
def setup_routes(app, gpio, mapping):
    relaycontroller = RelayController(gpio, mapping)
    app.router.add_get('/relays/', relaycontroller.relays)
    app.router.add_get('/relays/count', relaycontroller.num_relays)
    app.router.add_get('/relays/{relay}', relaycontroller.status)
    app.router.add_get('/relays/{relay}/state', relaycontroller.get_state, name='get_state')
    app.router.add_put('/relays/{relay}/state/{state}', relaycontroller.set_state, name='set_state')

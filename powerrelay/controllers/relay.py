from aiohttp import web
from powerrelay.drivers.gpio import IN, OUT, HIGH, LOW

class RelayController:
    """
        RelayAPI Controller
    """
    def __init__(self, gpio, relaymapping):
        self.gpio = gpio
        self.mapping = relaymapping
        self.relays_count = len(relaymapping)

    @staticmethod
    def relay_status(relay, value):
        if (relay['active'] == "high" and value == 1 or
            relay['active'] == "low" and value == 0):
            return "1"
        else:
            return "0"

    @staticmethod
    def try_intParse(value):
        try:
            return int(value), True
        except ValueError:
            return value, False

    async def relays(self,request):
        """
            Return the lines resources
        """
        relays = []
        for relay in self.mapping:
            relay_value = self.gpio.value(relay['chip'], relay['line'])
            relays.append({'id': relay['id'], 'state': RelayController.relay_status(relay,relay_value)})

        return web.json_response(relays)

    async def num_relays(self,request):
        """
            Return the number of relays
        """
        return web.json_response({"count": self.relays_count})

    async def status(self,request):
        """
            Relay status
        """
        try:
            relay = int(request.match_info['relay'])
            relay_mapped = next((x for x in self.mapping if x['id'] == relay),None)
            if relay_mapped == None:
                return web.HTTPError()

            relay_value = self.gpio.value(relay_mapped['chip'],relay_mapped['line'])
            res = {"relay_id": relay,
                   "status": RelayController.relay_status(relay_mapped,relay_value)
            }
            return web.json_response(res)
        except ValueError:
            return web.HTTPNotFound(text="Relay not found")

    async def get_state(self,request):
        """
            Relay get value
        """
        try:
            relay = int(request.match_info['relay'])
            relay_mapped = next((x for x in self.mapping if x['id'] == relay),None)
            if relay_mapped == None:
                return web.HTTPError()

            relay_value = self.gpio.value(relay_mapped['chip'],relay_mapped['line'])
            return web.json_response({"state": RelayController.relay_status(relay_mapped,relay_value)})

        except ValueError:
            return web.HTTPNotFound(text="Relay not found")

    async def set_state(self,request):
        """
            Relay set value
        """
        relay,status= RelayController.try_intParse(request.match_info['relay'])
        if not status:
            return web.HTTPNotFound(text="Relay not found")

        state_in,status = RelayController.try_intParse(request.match_info['state'])
        if not status:
            return web.HTTPNotFound(text="State invalid")

        if state_in < 0 or state_in > 1:
            return web.HTTPError()

        relay_mapped = next((x for x in self.mapping if x['id'] == relay),None)
        if relay_mapped == None:
            return web.HTTPError()

        if relay_mapped['active'] == 'high':
            self.gpio.output(relay_mapped['chip'],relay_mapped['line'], HIGH if state_in else LOW)
        elif relay_mapped['active'] == 'low':
            self.gpio.output(relay_mapped['chip'],relay_mapped['line'], LOW if state_in else HIGH)

        return web.json_response({"status": "ok"})

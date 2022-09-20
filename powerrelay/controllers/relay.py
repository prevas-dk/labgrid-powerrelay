from aiohttp import web
import json

class RelayController:
    """
        RelayAPI Controller
    """
    def __init__(self, lines):
        self.lines = lines
        self.line_count = len(lines)
        self.by_name = dict()
        for line in lines.values():
            name = line.name()
            if name:
                self.by_name[name] = line

    @classmethod
    def dumps(self, x):
        return json.dumps(x, indent=2) + "\n"

    @classmethod
    def json_response(self, data):
        return web.json_response(data, dumps=self.dumps)

    def lookup_line(self, s):
        # First try if it matches an id given in the config file
        if s in self.lines:
            return self.lines[s]
        if s in self.by_name:
            return self.by_name[s]
        raise web.HTTPNotFound(text="Relay '%s' not found" % s)

    async def relays(self,request):
        """
            Return the lines resources
        """
        relays = []
        for ident,line in self.lines.items():
            d = {'id': ident, 'state': str(line.get_value())}
            name = line.name()
            if name:
                d['name'] =  name
            relays.append(d)

        return self.json_response(relays)

    async def num_relays(self,request):
        """
            Return the number of relays
        """
        return self.json_response({"count": self.line_count})

    async def status(self,request):
        """
            Relay status
        """
        ident = request.match_info['relay']
        line = self.lookup_line(ident)

        value = line.get_value()
        res = {"relay_id": ident,
               "status": str(value)}
        return self.json_response(res)

    async def get_state_old(self,request):
        """
            Relay get value
        """
        import sys
        ident = request.match_info['relay']
        line = self.lookup_line(ident)

        return self.json_response({"state": str(line.get_value())})

    async def get_state(self,request):
        """
            Relay get value
        """
        import sys
        ident = request.match_info['relay']
        line = self.lookup_line(ident)

        return self.json_response(str(line.get_value()))


    async def set_state_old(self,request):
        """
            Relay set value
        """
        ident = request.match_info['relay']
        line = self.lookup_line(ident)

        try:
            value = int(request.match_info['state'])
            assert(0 <= value <= 1)
        except:
            raise web.HTTPBadRequest(text="Invalid state, must be 0 or 1")

        line.set_value(value)
        return self.json_response({"status": "ok"})

    async def set_state(self,request):
        """
            Relay set value
        """
        ident = request.match_info['relay']
        line = self.lookup_line(ident)

        try:
            value = int(await request.content.read())
            assert(0 <= value <= 1)
        except:
            raise web.HTTPBadRequest(text="Invalid state, must be 0 or 1")

        line.set_value(value)
        return self.json_response({"status": "ok"})

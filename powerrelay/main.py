#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Main module.
"""

# Note for future self: To run this directly on target during
# development without going through all the setuptools yoga and
# getting stuff installed in the right places, one can just scp the
# whole tree and then do
#
#   python3 -m powerrelay.main run ./config.yaml

import sys
import asyncio
import logging
import click
import errno
import os
from dataclasses import dataclass

import trafaret_config as traf_cfg
import trafaret as t

from aiohttp import web

import gpiod

from gpiod.line import Direction, Value
from gpiod.line_request import LineRequest
from gpiod.chip import Chip

from . import routes

CONFIG_TRAFARET = t.Dict(
    {
        t.Key("host"): t.String(),
        t.Key("port"): t.Int(),
        t.Key("relays"): t.Mapping(
            t.String(),
            t.Dict(
                {
                    t.Key("chip", optional=True): t.String(),
                    t.Key("line", optional=True): t.Int(),
                    t.Key("name", optional=True): t.String(),
                    t.Key("active", optional=True, default='high'): t.Enum('high', 'low'),
                    t.Key("default", optional=True, default=0): t.Int(),
                }
            )
        ),
    }
)

class TrafaretYaml(click.Path):
    """
        Configuration read from YAML file checked against trafaret rules.
    """
    name = "trafaret yaml file"

    def __init__(self, trafaret):
        self.trafaret = trafaret
        super().__init__(
            exists=True, file_okay=True, dir_okay=False, readable=True)

    def convert(self, value, param, ctx):
        cfg_file = super().convert(value, param, ctx)
        try:
            return traf_cfg.read_and_validate(cfg_file, self.trafaret)
        except traf_cfg.ConfigError as e:
            msg = "\n".join(str(err) for err in e.errors)
            self.fail("\n" + msg)

@dataclass
class RelayLine:
    request: LineRequest
    offset: int
    name: str

def validate_relays(relays):
    """
        Validate that each relay specifies either chip,line or name
    """
    for ident,cfg in relays.items():
        has_chip_line = "chip" in cfg and "line" in cfg
        has_name = "name" in cfg
        if has_chip_line and has_name:
            return (False, "Relay %s: cannot specify both GPIO name and chip name+line number" % ident)
        if not has_chip_line and not has_name:
            return (False, "Relay %s: must specify either GPIO name or chip name+line number" % ident)
    return (True, None)

# If the gpio name is set, we need to browse through all
# gpiochip devices and (hopefully) find the device. For
# unknown reasons, the ability "find_line" ability has been
# removed in libgpiod 2.0.
# If the chipname is set, it becomes quite easy, since we can
# just use the chipname and offset directly
def cfg_to_gpiochip_and_offset(cfg):
    if 'name' in cfg:
        name = cfg['name']
        for entry in os.scandir("/dev/"):
            if gpiod.is_gpiochip_device(entry.path):
                with gpiod.Chip(entry.path) as chip:
                    offset = chip.line_offset_from_id(name)
                    if offset is not None:
                        return chip.get_info().name, offset
        raise Exception("No such GPIO")
    else:
        return cfg['chip'], cfg['line']

# I'm tired of my terminal getting messed up when testing using 'curl -v -X GET ...'
@web.middleware
async def terminate_exception_body_by_newline(request, handler):
    try:
        response = await handler(request)
        return response
    except web.HTTPException as ex:
        text = ex.text
        if isinstance(text, str):
            if not text.endswith("\n"):
                ex.text = text + "\n"
        raise ex

@click.group()
def powerrelay():
    pass

@powerrelay.command()
@click.argument("config", type=TrafaretYaml(CONFIG_TRAFARET))
def validate(config):
    """
        Validate configuration file structure.
    """
    valid, error = validate_relays(config['relays'])
    if not valid:
        click.echo("Error: Configuration invalid: {}".format(error))
    else:
        click.echo("OK: Configuration is valid.")

@powerrelay.command()
@click.argument("config", type=TrafaretYaml(CONFIG_TRAFARET))
def run(config):
    """
        PowerRelay
    """
    try:
        host = config["host"]
        port = config["port"]
        relays = config["relays"]

        # validate relay mapping
        validate_relays(relays)

        logging.basicConfig(level=logging.ERROR)

        # setup application and extensions
        app = web.Application(middlewares=[terminate_exception_body_by_newline])

        # setup gpio line instances
        lines = dict()
        for ident,cfg in relays.items():
            gpiochip, offset = cfg_to_gpiochip_and_offset(cfg)
            if cfg['active'] == 'low':
                active_low=True
            else:
                active_low=False
            gpiochip_path = "/dev/" + gpiochip
            request = gpiod.request_lines(gpiochip_path, consumer="PowerRelay", config={tuple([offset]): gpiod.LineSettings(direction=Direction.OUTPUT, active_low=active_low)})
            chip = gpiod.Chip(gpiochip_path)
            linename=""
            if 'name' in cfg:
                linename=cfg['name']
            lines[ident] = RelayLine(request, offset, linename)

        # Only set the defaults when we've succesfully requested all lines.
        for ident in lines:
            lines[ident].request.set_values({lines[ident].offset: Value(relays[ident]['default'])})

        # setup routes
        routes.setup_routes(app, lines)

        web.run_app(app, host=host, port=port)

    except OSError as ex:
        print(str(ex), file=sys.stderr)
        sys.exit(1)
    except traf_cfg.ConfigError as ex:
        ex.output()
        sys.exit(1)

if __name__ == "__main__":
    powerrelay()

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

import trafaret_config as traf_cfg
import trafaret as t

from aiohttp import web
import aiohttp_jinja2
import jinja2

import gpiod

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

# Unfortunately, the python bindings for libgpiod have slightly
# inconsistent way of reporting errors:
#
# - Looking up a line by name return None if there's no such line.
#
# - Looking up a non-existent chip raises ENOENT.
#
# - Asking for a non-existent line from a gpiod.Chip raises EINVAL.
#
# Try to normalize all these cases to ENOENT aka FileNotFoundError,
# and put some reasonable stuff in the exception object's strerror.
def cfg_to_line(cfg):
    if 'name' in cfg:
        name = cfg['name']
        line = gpiod.find_line(name)
        if not line:
            raise FileNotFoundError(errno.ENOENT, "No such GPIO line", name)
    else:
        try:
            chip = gpiod.Chip(cfg['chip'], gpiod.Chip.OPEN_LOOKUP)
            line = chip.get_line(cfg['line'])
        except FileNotFoundError as e:
            e.strerror = "No such GPIO chip"
            e.filename = cfg['chip']
            raise e
        except OSError as e:
            if e.errno == errno.EINVAL:
                raise FileNotFoundError(errno.ENOENT, "GPIO chip '%s' has no line %d" %
                                        (cfg['chip'], cfg['line']))
            raise e
    return line

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

        # setup jinja template
        aiohttp_jinja2.setup(app, loader=jinja2.PackageLoader('powerrelay','views'))

        # setup gpio line instances
        lines = dict()
        for ident,cfg in relays.items():
            line = cfg_to_line(cfg)
            flags = 0
            if cfg['active'] == 'low':
                flags |= gpiod.LINE_REQ_FLAG_ACTIVE_LOW
            line.request(consumer="PowerRelay", type=gpiod.LINE_REQ_DIR_OUT, flags=flags)
            lines[ident] = line

        # Only set the defaults when we've succesfully requested all lines.
        for ident in lines:
            lines[ident].set_value(relays[ident]['default'])

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

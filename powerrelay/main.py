#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Main module.
"""

import sys
import asyncio
import logging
import click

import trafaret_config as traf_cfg
import trafaret as t

from aiohttp import web
import aiohttp_jinja2
import jinja2

from powerrelay.drivers import libgpiod, GPIOLineInUsedError, GPIOInvalidLineError
from . import routes, middleware

CONFIG_TRAFARET = t.Dict(
    {
        t.Key("host"): t.String(),
        t.Key("port"): t.Int(),
        t.Key("relays"): t.List(
            t.Dict(
                {
                    t.Key("id"): t.Int(),
                    t.Key("chip"): t.String(),
                    t.Key("line"): t.Int(),
                    t.Key("active"): t.String(),
                    t.Key("default"): t.Int(),
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

def unique_list(var):
    """
        Returns true if the list is unique.
    """
    return len([x for x in set(var)]) == len(var)

def validate_relays(mapping):
    """
        Validate that we dont have any duplicates
    """
    if not unique_list([ x['id'] for x in mapping ]):
        return (False, "relay id's not unique")

    chip_lines = [ (x['chip'],x['line']) for x in mapping ]
    for idx, val in enumerate(chip_lines):
        if chip_lines[idx] in chip_lines[idx+1:]:
            return (False, "relay chip,line duplication")

    return (True, None)

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
        mapping = config["relays"]

        # validate relay mapping
        validate_relays(mapping)

        logging.basicConfig(level=logging.ERROR)
        loop = asyncio.get_event_loop()

        # setup application and extensions
        app = web.Application(loop=loop)

        # setup jinja template
        aiohttp_jinja2.setup(app, loader=jinja2.PackageLoader('powerrelay','views'))

        # setup gpio chips
        gpio_instances = dict()
        chips = set()
        for relay_mapping in mapping:
            for key, value in relay_mapping.items():
                if key == 'chip':
                    chips.add(value)
                    gpio_instances[value] = libgpiod.GPIO(value)

        # set lines to output
        for relay_mapping in mapping:
            chip = relay_mapping['chip']
            line = relay_mapping['line']
            default = relay_mapping['default']
            gpio_instances.get(chip).output(line, default)

        # setup views and routes
        routes.setup_routes(app, gpio_instances, mapping)
        middleware.setup_middleware(app)

        web.run_app(app, host=host, port=port)

    except GPIOInvalidLineError as ex:
        pass
    except GPIOLineInUsedError as ex:
        pass
    except traf_cfg.ConfigError as ex:
        ex.output()
        sys.exit(1)

if __name__ == "__main__":
    powerrelay()

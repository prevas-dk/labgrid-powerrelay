#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Tests for `powerrelay` package."""

import pytest

from click.testing import CliRunner

from powerrelay import main

@pytest.fixture
def response():
    """
        Sample pytest fixture.
    """

def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(main.main)
    assert result.exit_code == 2

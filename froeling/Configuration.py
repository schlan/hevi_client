#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

from froeling.FroelingValueConverter import *
from configparser import ConfigParser
from sys import exit
from pathlib import Path
import logging

class HeviConfig(object): 
  def __init__(self, path):
    parser = ConfigParser()
    parser.read_file(path)

    if parser.has_section('Main'):
      self._exit_if_missing('Main', ['device_token', 'port'], parser)
      self.device_token = parser.get('Main', 'device_token')
      self.port = parser.get('Main', 'port')
      self._exit_if_file_missing(self.port)
      self.heating_circuits = self._extract_circuits(parser)
    else:
      self._exit_with_error('Unable to parse configuration file, [Main] section not found')
  

  def _extract_circuit_values(self, section, name, config):
    if config.has_option(section, name):
      return { name: ast.literal_eval(config.get(section, name)) }
    else:
      return None

  def _extract_single_circuit(self, parser, section):
    options = ["pump", "flow_actual", "flow_shall", "mixer_on", "mixer_off", "party"]
    data = list(map(lambda x: self._extract_circuit_values(section, x, parser), options))
    result = dict()
    for x in data:
      if x:
        for y in x:
          result[y] = x[y]
    return { section.split("|")[1]: result }

  def _extract_circuits(self, parser):
    hc_config = list(filter(lambda x: x.startswith("hevi_hc|"), parser.sections()))
    config = list(map(lambda x: self._extract_single_circuit(parser, x), hc_config))
    result = dict()
    for x in config:
      for y in x:
        result[y] = x[y]
    return result

  def _exit_if_file_missing(self, path):
    path = Path(path)
    if not path.exists():
      self._exit_with_error("Port not available ({0})".format(path))

  def _exit_if_missing(self, section, args, parser):
    for option in args:
      if not parser.has_option(section, option):
        self._exit_with_error("Mandatory option is missing in section [{0}]: `{1}`".format(section, option))

  def _exit_with_error(self, msg):
    logging.error(msg)
    exit(1)  
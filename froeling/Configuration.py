#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

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
    else:
      self._exit_with_error('Unable to parse configuration file, [Main] section not found')
  
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
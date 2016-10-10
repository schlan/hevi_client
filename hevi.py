#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import time, json, sys, logging
from logging.handlers import RotatingFileHandler

from argparse import ArgumentParser, FileType 
from datetime import datetime
from pathlib import Path

from froeling.FroelingValueConverter import *
from froeling.FroelingClient import FroelingClient
from froeling.Configuration import HeviConfig
from froeling.Network import Network
from froeling.HostInfo import host_info

from froeling.HeatingCircuitGenerator import print_circuit_config

from version import VERSION_STRING

def parse_arguments():
  parser = ArgumentParser()
  parser.add_argument("--config", help="Path to the configuration file", type=FileType('r'), required=True)
  parser.add_argument("-v", "--verbose", help="Enable verbose logging", required=False, action='store_true')
  parser.add_argument('--version', help='Show hevi version', action='store_true')

  group = parser.add_mutually_exclusive_group(required=False)
  group.add_argument('--submit', help='Load data and submit it to froeling.io', action='store_true')
  group.add_argument('--test', help='Test connection to heating', action='store_true')
  group.add_argument('--values', help='Load and display all recent values', action='store_true')
  group.add_argument('--schema', help='Load recent values schema', action='store_true')
  group.add_argument('--state', help='Lost state', action='store_true')
  group.add_argument('--errors', help='Load errors', action='store_true')
  group.add_argument('--menu', help='Load menu structure', action='store_true')
  group.add_argument('--genconfig', help='Genarte extra config', action='store_true')
  group.add_argument('--date', help='Load device date and version', action='store_true')

  args = parser.parse_args()
  return args
  
def init_logger(debug):
  root = logging.getLogger()

  level = logging.INFO
  if debug:
    level = logging.DEBUG

  root.setLevel(level)

  log_path = Path.home().joinpath('.hevi', 'hevi.log')
  if not log_path.parent.exists():
    log_path.parent.mkdir(parents=True)

  file_handler = RotatingFileHandler(str(log_path), maxBytes=102400, backupCount=5)
  file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)8s - %(message)s'))
  root.addHandler(file_handler)

  console_handler = logging.StreamHandler(sys.stdout)
  console_handler.setFormatter(logging.Formatter('[%(levelname)8s] %(message)s'))
  root.addHandler(console_handler)

def query_data_and_submit(config):
  client = FroelingClient(config.port)
  
  # Load errors
  errors = client.load_errors()
  logging.info("Boiler errors loaded ({0})".format(len(errors)))

  # Load schema + values
  schema = client.load_recent_values_schema()
  logging.info("Value schemas loaded ({0})".format(len(schema)))

  values = client.load_recent_values(schema)
  logging.info("Boiler values loaded ({0})".format(len(values)))

  for s in schema:
    s['address'] = fr_hex(s['address'])

  # Load status info
  version = client.load_version_date()
  logging.info("Boiler version/date loaded")
  state = client.load_state()
  logging.info("Boiler state received")
  state['version'] = version['version']

  # heating circuits
  logging.info("Load heating circuits info")
  hc = _heating_circuits_config_to_json(config.heating_circuits)
  digital_outputs = _load_digital_output(client, _find_digital_output_items(config.heating_circuits))

  logging.info("Load host info")
  host = host_info()

  data = {
    'timestamp': int(time.time()),
    'recent_values_schema': schema,
    'recent_values': values,
    'errors': errors,
    'status': state,
    'host_state': host,
    'digital_outputs': digital_outputs,
    'heating_circuits': hc
  }

  print(json.dumps(data))
  
  logging.info("Sending data to froeling.io")
  network = Network(config.device_token)
  network.send_data(data)

def _load_digital_output(client, menuitems):
  result = []
  for item in menuitems:
    data = client.load_digital_output(item['address'])
    if data:
      result.append({
        **data,
        'description': item['description'],
        'address': fr_hex(item['address'])
      })
  return result

def _find_digital_output_items(circuits):
  digital_outputs = []
  for c in circuits:
    circuit = circuits[c]
    for i in circuit:
      if circuit[i]['type'] == 17:
        digital_outputs.append(circuit[i])
  return digital_outputs

def _menuitem_to_json(menuitem):
  return {
    'description': menuitem['description'],
    'address': fr_hex(menuitem['address']),
    'type': menuitem['type']
  }

def _heating_circuits_config_to_json(circuits):
  new_circuits = {}
  for c in circuits:
    circuit = circuits[c]
    new_circuit = dict()
    for i in circuit:
      new_circuit[i] = _menuitem_to_json(circuit[i])
    new_circuits[c] = new_circuit
  return new_circuits


def test_connection(config):
  client = FroelingClient(config.port)
  logging.info(client.test_connection())

def values(config):
  client = FroelingClient(config.port)
  schema = client.load_recent_values_schema()
  values = client.load_recent_values(schema)

  for address in values:
    s = list(filter(lambda x: fr_hex(x['address']) == address, schema))
    if len(s) > 0:
      v = values[address]
      logging.info("{0} ({1}): {2}{3}".format(s[0]['description'], fr_hex(s[0]['address']), v, s[0]['unit']))

def schema(config):
  client = FroelingClient(config.port)
  schema = client.load_recent_values_schema()
  
  for s in schema:
    logging.info("{0} | Address: {1} | Unit: {2} | Factor: {3}".format(s['description'], fr_hex(s['address']), s['unit'], s['factor']))

def state(config):
  client = FroelingClient(config.port)
  state = client.load_state()
  logging.info("Mode: {0} | State: {1}".format(state['mode'], state['state']))

def errors(config):
  client = FroelingClient(config.port)
  errors = client.load_errors()

  for e in errors:
    t = datetime.fromtimestamp(e['timestamp']).isoformat()
    logging.info("{0} | Number: {1} | State: {2} | Info: {3} | Timestamp: {4}".format(e['description'], e['number'], e['state'], e['info'], t))

def menu(config):
  client = FroelingClient(config.port)
  menu_entries = client.load_menu_structure()
  for m in menu_entries:
    logging.info("{0} | Type: {1} | Address: {2} | Parent: {3} | Child: {4}".format(m['description'], m['type'], fr_hex(m['address']),fr_hex(m['parent']),fr_hex(m['child'])))

def date(config):
  client = FroelingClient(config.port)
  date = client.load_version_date()
  t = datetime.fromtimestamp(date['timestamp']).isoformat()
  logging.info("Version: {0} | Date: {1}".format(date['version'], t))

def gen_config(config):
  client = FroelingClient(config.port)
  menu = client.load_menu_structure()
  print_circuit_config(menu)

def version():
  logging.info(VERSION_STRING)

if __name__ == "__main__":
  args = parse_arguments()
  init_logger(args.verbose)
  config = HeviConfig(args.config)

  if args.version:
    version()
  elif args.submit:
    query_data_and_submit(config)
  elif args.test:
    test_connection(config)
  elif args.values:
    values(config)
  elif args.schema:
    schema(config)
  elif args.state:
    state(config)
  elif args.errors:
    errors(config)
  elif args.menu:
    menu(config)
  elif args.date:
    date(config)
  elif args.genconfig:
    gen_config(config)
  else:
    logging.info("Please provide an argument")
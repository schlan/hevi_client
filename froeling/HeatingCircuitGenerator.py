#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import configparser, sys, functools, logging

def print_circuit_config(menu):
  heat = findItemByName(findSubMenuItems(menu, b'\x00\x01'), "Heizen")

  if heat is None:
    logging.info("Unable to read menu ... boiler language shall be german. Please contact admin@froeling.io")
    return
  
  heat_items = findSubMenuItems(menu, heat['child'])
  circuits = list(filter(lambda x: x['description'].startswith("Heizkreis"), heat_items))

  config = list(map(lambda x: heating_circuites(menu, x['description'], x['child']), circuits))
  parser = configparser.ConfigParser()
  for x in config:
    for y in x:
      parser['hevi_hc|' + y] = x[y]
  
  print("Plase append the following to your existing configuration:")
  print()
  print()
  parser.write(sys.stdout)
  print()
  print()
  
def findSubMenuItems(menu, child):
  return list(filter(lambda x: x['parent'] == child, menu))

def findItemByName(menu, name):
  result = list(filter(lambda x: x['description'] == name, menu))
  if len(result) > 0:
    return result[0]
  else:
    None

def toConfig(item, name):
  if item:
    return {
      name + '_address' : str(item['address']),
      name + '_type' : str(item['type']),
      name + '_description' : str(item['description'])
    }
  else: 
    return {}

def heating_circuites(menu, name, child):
  sub_menu = findSubMenuItems(menu, child)

  state = findItemByName(sub_menu, "Zustand")
  state_items = findSubMenuItems(menu, state['child'])

  party = findItemByName(state_items, "Partyschalter")  
  flow_shall = findItemByName(state_items, "Vorlauf-Solltemperatur")
  flow_actual = findItemByName(state_items, "Vorlauf-Isttemperatur")

  service = findItemByName(sub_menu, "Service")
  service_items = findSubMenuItems(menu, service['child'])
  pump = findItemByName(service_items, "Heizkreispumpe")
  mixer_on = findItemByName(service_items, "HK Mischer AUF")
  mixer_off = findItemByName(service_items, "HK Mischer ZU")

  return {
    name: {
      'pump': pump,
      'party': party,
      'mixer_off': mixer_off,
      'mixer_on': mixer_on,
      'flow_shall': flow_shall,
      'flow_actual': flow_actual
    }
  }
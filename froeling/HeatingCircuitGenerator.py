#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import configparser, sys, functools, logging

def print_circuit_config(menu):
  heat = findItemByName(findSubMenuItems(menu, b'\x00\x01'), "Heizen")

  if heat is None:
    logging.info("Unable to read menu ... boiler language must be German. Please contact admin@froeling.io")
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

def heating_circuites(menu, name, child):
  data = {}
  data[name] = {}

  sub_menu = findSubMenuItems(menu, child)

  state = findItemByName(sub_menu, "Zustand")
  if state:
    state_items = findSubMenuItems(menu, state['child'])
    party = findItemByName(state_items, "Partyschalter")
    room_temp = findItemByName(state_items, "Raumtemperatur")
    flow_target = findItemByName(state_items, "Vorlauf-Solltemperatur")
    flow_actual = findItemByName(state_items, "Vorlauf-Isttemperatur")

    if party:
      data[name]['party'] = party
    if room_temp:
      data[name]['room_temp'] = room_temp
    if flow_target:
      data[name]['flow_target'] = flow_target
    if flow_actual:
      data[name]['flow_actual'] = flow_actual

  service = findItemByName(sub_menu, "Service")
  if service:
    service_items = findSubMenuItems(menu, service['child'])
    pump = findItemByName(service_items, "Heizkreispumpe")
    mixer_on = findItemByName(service_items, "HK Mischer AUF")
    mixer_off = findItemByName(service_items, "HK Mischer ZU")
  
    if pump:
      data[name]['pump'] = pump
    if mixer_on:
      data[name]['mixer_on'] = mixer_on
    if mixer_off:
      data[name]['mixer_off'] = mixer_off

  return data
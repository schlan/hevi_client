#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import string
import binascii
import ast
from datetime import datetime

def fr_string(bytes):
  return fr_strip(bytes.decode("ISO-8859-1", errors='replace'))

def fr_bytes(string):
  return bytes(string, "ISO-8859-1")

def fr_strip(value):
  return value.strip()

def fr_int(value, signed = False):
  return int.from_bytes(value, byteorder='big', signed = signed)

def fr_hex(value):
  return fr_string(binascii.hexlify(value))

def fr_parse_byte_string(value):
  return ast.literal_eval(value)

def fr_timestamp(value):
  def ensure_one(value):
    if value is 0:
      return 1
    else:
      return value
  
  def ensure_two_digits(value):
    if value < 10:
      return str(0) + str(value)
    else:
      return str(value)

  seconds = ensure_two_digits(value[0])
  minutes = ensure_two_digits(value[1])
  hours = ensure_two_digits(value[2])
  time = str(hours) + ':' + str(minutes) + ':' + str(seconds)

  day = value[3]
  month = value[4]
  year = value[len(value) - 1]
  date = ensure_two_digits(ensure_one(day)) + "." + ensure_two_digits(ensure_one(month)) + "." + ensure_two_digits(year)
  return int(datetime.strptime(time + " " + date, '%H:%M:%S %d.%m.%y').timestamp())

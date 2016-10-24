#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import string
import binascii
import ast

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
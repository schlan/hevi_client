#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import string
import binascii

def fr_string(bytes):
  return fr_strip(bytes.decode("ISO-8859-1", errors='replace'))

def fr_bytes(string):
  return bytes(string, "ISO-8859-1")

def fr_strip(value):
  return value.strip()

def fr_int(value):
  return int.from_bytes(value, byteorder='big')

def fr_hex(value):
  return fr_string(binascii.hexlify(value))
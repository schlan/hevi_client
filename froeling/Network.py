#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

from urllib.request import Request, urlopen
import json, logging
class Network(object):

  def __init__(self, device_token):
    self.server = "https://froeling.io"
    self.device_token = device_token

  def send_data(self, data):
    url = '{0}/api/values'.format(self.server)
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + self.device_token}
    payload = json.dumps(data).encode('utf8')
    request = Request(url, data = payload, headers = headers)
    with urlopen(request) as response:
      logging.info("Data sent | Code: {0} | Body {1}".format(response.getcode(), str(response.read())))
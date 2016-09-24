#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

from collections import OrderedDict
from serial import Serial
from time import sleep
import binascii, logging

class SerialClient(object):

  def __init__(self, port):
    self.serial_port = port
    self.frame_header = bytes(b'\x02\xfd')
    
    self.forward_replace = OrderedDict([(b'\x2b', b'\x2b\x00'), (b'\xfe', b'\xfe\x00'), (b'\x02', b'\x02\x00'), (b'\x11', b'\xfe\x12'), (b'\x13', b'\xfe\x14')])
    self.backward_replace = OrderedDict(reversed([(b'\x2b\x00', b'\x2b'), (b'\xfe\x00', b'\xfe'), (b'\x02\x00', b'\x02'), (b'\xfe\x12', b'\x11'), (b'\xfe\x14', b'\x13')]))

    self.retry_count = 10
    self.ser = Serial(port, 57600, timeout = None)

  def single_communication(self, address, body):
    self.ser.close() 
    self.ser.open()
    self.ser.isOpen()

    frame = self._build_frame(address, body)
    result = self._sendFrame(frame, self.ser)
    self.ser.close()

    if result['verified'] is True:
      return self._decode_frame(result['value'])
    else:
      return None
    
    
  def multiple_communication(self, initial_address, initial_body, address, body): 
    self.ser.close() 
    self.ser.open()
    self.ser.isOpen()

    first_frame = self._build_frame(initial_address, initial_body)
    base_frame = self._build_frame(address, body)

    first_result = self._sendFrame(first_frame, self.ser)

    valid_responses = []
    invalid_responses = []

    if first_result["verified"] is True:
      valid_responses.append(self._decode_frame(first_result["value"]))
    else:
      invalid_responses.append(first_result["value"])

    while True:
      response = self._sendFrame(base_frame, self.ser)
      end_frame_found = False
      
      if response['verified'] is True:
        frame = self._decode_frame(response["value"])
        valid_responses.append(frame)
        if frame['body'] == b'\x00':
          end_frame_found = True
      else:
        logging.warning("Invalid response: " + str(response["value"]))
        invalid_responses.append(response["value"])

      if end_frame_found is True:
        break
  
    self.ser.close()

    recovered_responses = self._recover_invalid_responses(invalid_responses)
    logging.debug("recovered_responses: " + str(len(recovered_responses)))

    for rr in recovered_responses:
      valid_responses.append(rr)
    
    return self._remove_duplicates(valid_responses)

  def _sendFrame(self, frame, serial):
    result = b''
    count = 0

    logging.debug("TX: " + str(binascii.hexlify(frame)))
    serial.write(frame)
    serial.flush()

    result = b''
    holdon = 0
    while serial.inWaiting() > 0 or holdon == 0:
      if serial.inWaiting() == 0:
        sleep(0.05)
        holdon = 1
      else:
        result = result + serial.read(serial.inWaiting())

    logging.debug("RX: " + str(binascii.hexlify(result)))
    return_value = {"verified": True, "value": result}

    if self._verify_response(result) is True:
      if count > self.retry_count:
        logging.warning("Tried to send frame 10 times, it's not working :(")
        return_value = {"verified": False, "value": frame}
    else:
      logging.warning("RX: invalid frame")
      return_value = {"verified": False, "value": result}

    return return_value
  
  def _recover_invalid_responses(self, frames):
    merged = b''
    for f in frames:
      merged = merged + f

    header = self._find_header(merged)
    new_frames = self._split_frame(merged, header)
    new_valid_frames = []

    for f in new_frames:
      if self._verify_response(f) is True:
        new_valid_frames.append(self._decode_frame(f))
    return new_valid_frames

  def _find_header(self, frame):
    index = 0
    indices = []
    while frame.find(self.frame_header, index) != -1:
      indices.append(frame.find(self.frame_header, index))
      index = frame.find(self.frame_header, index) + 1
    return indices

  def _split_frame(self, frame, indices):
    frames = []
    for i, index in enumerate(indices):
      if i < len(indices) - 1:
        frames.append(frame[index:indices[i+1]])
      elif i == len(indices) -1:
        frames.append(frame[index:])
    return frames

  def _remove_duplicates(self, responses): 
    return list({v['body']:v for v in responses}.values())

  def _verify_response(self, response):
    if len(response) > 5 and self._decode_frame(response)['header'] == self.frame_header:
      frame = self._decode_frame(response)
      crc = self._crc(frame['header'] + frame['length'] + frame['address'].to_bytes(1, byteorder='big') + frame['body'])

      if crc == frame['crc'] and self._frame_length(frame['body']) == frame['length']:
        return True
      else: 
        if crc != frame['crc']:
          logging.warning("Verify: crc mismatch")
        if self._frame_length(frame['body']) == frame['length']:
          logging.warning("Verify: Frame length mismatch")
        return False

    else:
      if len(response) > 5 and self._decode_frame(response)['header'] != self.frame_header:
        logging.warning("Verify: Frame hasn't the right header")
      elif len(response) < 5:
        logging.warning("Verify: Frame is too short")
      return False

  def _decode_frame(self, frame):
    frame = self._backward_replace_bytes_in_frame(frame)
    return {'header': frame[:2], 'length': frame[2:4], 'address': frame[4], 'crc': frame[len(frame)-1:], 'body': frame[5:len(frame)-1]}

  def _backward_replace_bytes_in_frame(self, frame):
    return self._replace_bytes(frame, self.backward_replace)

  def _forward_replace_bytes_in_frame(self, frame):
    return self._replace_bytes(frame, self.forward_replace)
    
  def _replace_bytes(self, frame, map):
    new_frame = frame[2:]
    for k in map:
      new_frame = new_frame.replace(k, map[k])
    return frame[:2] + new_frame

  def _build_frame(self, address, body):
    raw_frame = self.frame_header + self._frame_length(body) + address + body
    crc_frame = raw_frame + self._crc(raw_frame)
    return self._forward_replace_bytes_in_frame(crc_frame) 

  def _frame_length(self, body):
    return (len(body) + 1).to_bytes(2, byteorder='big')

  def _crc(self, frame):
    crc = 0
    for c in frame:
      crc = crc ^ (c * 2) & 255 ^ c    
    return crc.to_bytes(1, byteorder='big')
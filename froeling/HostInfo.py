import os, psutil

def host_info():
  return {
    **_cpu_load(),
    **_memory(),
    **_disk_root(),
    **_uptime()
  }

def _cpu_load():
  load = os.getloadavg()
  return { 'cpu_load': '|'.join(str(i) for i in load) }

def _memory():
  mem = psutil.virtual_memory()
  return {
    'mem_free': mem.free,
    'mem_total': mem.total,
    'mem_available': mem.available,
    'mem_percent': mem.percent,
    'mem_used': mem.used
  }

def _disk_root():
  disk = psutil.disk_usage("/")
  return {
    'disk_total': disk.total,
    'disk_used': disk.used,
    'disk_free': disk.free,
    'disk_percent': disk.percent
  }

def _uptime():
  return { 'boot_time': int(psutil.boot_time()) }
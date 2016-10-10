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
    'mem_free': str(mem.free),
    'mem_total': str(mem.total),
    'mem_available': str(mem.available),
    'mem_percent': str(mem.percent),
    'mem_used': str(mem.used)
  }

def _disk_root():
  disk = psutil.disk_usage("/")
  return {
    'disk_total': str(disk.total),
    'disk_used': str(disk.used),
    'disk_free': str(disk.free),
    'disk_percent': str(disk.percent)
  }

def _uptime():
  return { 'boot_time': str(int(psutil.boot_time())) }
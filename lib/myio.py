logname= 'pythonapp'
import traceback

def log_exception(*extra):
  global logname;  logspec= '/dev/shm/'+ logname+ '.except.log'
  exc_type, exc_value, exc_tb = sys.exc_info()
  stre= str(exc_type)
  tbe = traceback.TracebackException(exc_type, exc_value, exc_tb)
  o = open(logspec, 'w')
  o.write(stre)
  for line in tbe.format():  o.write(line)
  for line in extra:  o.write(str(line))
  o.close()
  os.system('pluma '+ logspec+ ' &')

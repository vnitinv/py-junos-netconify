import serial
import re
from time import sleep
from datetime import datetime, timedelta

from .tty_terminal import Terminal

##### -------------------------------------------------------------------------
##### Terminal connection over SERIAL CONSOLE
##### -------------------------------------------------------------------------

_PROMPT = re.compile('|'.join(Terminal._RE_PAT))

class Serial(Terminal):

  def __init__(self, port='/dev/ttyUSB0', **kvargs):
    """
    :port:
      the serial port, defaults to USB0 since this

    :kvargs['timeout']:
      this is the tty read polling timeout.  
      generally you should not have to tweak this.      
    """
    # initialize the underlying TTY device

    self.port = port
    self._ser = serial.Serial()    
    self._ser.port = port
    self._ser.timeout = kvargs.get('timeout', self.TIMEOUT)

    Terminal.__init__(self, **kvargs)

  ### -------------------------------------------------------------------------
  ### I/O open close called from Terminal class
  ### -------------------------------------------------------------------------

  def _tty_open(self):
    self._ser.open()    
    self.write('\n\n\n')      # hit <ENTER> a few times, yo!    

  def _tty_close(self):
    self._ser.close()

  ### -------------------------------------------------------------------------
  ### I/O read and write called from Terminal class
  ### -------------------------------------------------------------------------

  def write(self, content):
    self._ser.write(content+'\n')
    self._ser.flush()

  def read_prompt(self):
    """
    reads text from the serial console (using readline) until
    a match is found against the :expect: regular-expression object.
    When a match is found, return a tuple(<text>,<found>) where
    <text> is the complete text and <found> is the name of the 
    regular-expression group. If a timeout occurs, then return 
    the tuple(None,None).
    """
    rxb = ''
    mark_start = datetime.now()
    mark_end = mark_start + timedelta(seconds=self.EXPECT_TIMEOUT)

    while datetime.now() < mark_end:
      sleep(0.1)                          # do not remove
      line = self._ser.readline()
      if not line: continue
      rxb += line
      found = _PROMPT.search( rxb ) 
      if found is not None: break         # done reading
    else:
      # exceeded the while loop timeout
      return (None,None)

    return (rxb, found.lastgroup)   

  ### -------------------------------------------------------------------------
  ### I/O LOW-LEVEL read and write called internally
  ### -------------------------------------------------------------------------

  def _tty_rawwrite(self,content):
    self._ser.write(content)

  def _tty_flush(self):
    self._ser.flush()        

  def _tty_dev_read(self):
    return self._ser.readline()  
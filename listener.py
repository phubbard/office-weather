#!/usr/bin/env python

# pfh 6/15/09
# Starting from http://itamarst.org/writings/etech04/twisted_internet-22.html
# Goal: Listen to arduino, save data in engineering units, to CSV, also present
# in twisted.web or similar. Socket server?
#
# Design: For now, have arduino send raw ADC counts over and we'll do the
# calibration - seems smarter. I can then use config file parser to move
# all the constants into a config file.
#
# I really want something like rrdtool-based graphs with different timescales.
# Maybe graphite?
# http://somic.org/2009/05/21/graphite-rabbitmq-integration/
# Or even AMQP for fun?
# Serial code from http://twistedmatrix.com/projects/core/documentation/examples/gpsfix.py

from twisted.protocols.basic import LineReceiver

from twisted.internet import reactor
from twisted.internet.serialport import SerialPort

from twisted.python import usage
import logging
import sys


class THOptions(usage.Options):
    optParameters = [
        ['baudrate', 'b', 9600, 'Serial baudrate'],
        ['port', 'p', '/dev/tty.usbserial-A6008hB0', 'Serial port to use'],
        ]

class Echo(LineReceiver):
    def processData(self, data):
        """Convert raw ADC counts into SI units as per datasheets"""
        if len(data) != 2:
            return

        tempCts = int(data[0])
        rhCts = int(data[1])

        rhVolts = rhCts * 0.0048828125
        # 10mV/degree, 1024 count/5V
        temp = tempCts * 0.48828125
        # TODO need to rewrite this to include thermal compensation as per SC600 datasheet!
        humidity = (rhVolts * 45.25) - 42.76
        logging.info('Temp: %f C Relative humidity: %f %%' % (temp, humidity))
        logging.debug('Temp: %f counts: %d RH: %f counts: %d volts: %f' % (temp, tempCts, humidity, rhCts, rhVolts))
        return temp, humidity

    def connectionMade(self):
        logging.info('Connection made!')

    def lineReceived(self, line):
        try:
            data = line.split()
            logging.debug(data)
            self.processData(data)
        except ValueError:
            logging.error('Unable to parse data %s' % line)
            return

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, \
                format='%(asctime)s %(levelname)s [%(funcName)s] %(message)s')

    o = THOptions()
    try:
        o.parseOptions()
    except usage.UsageError, errortext:
        logging.error('%s %s' % (sys.argv[0], errortext))
        logging.info('Try %s --help for usage details' % sys.argv[0])
        raise SystemExit, 1

    if o.opts['baudrate']:
        baudrate = int(o.opts['baudrate'])

    port = o.opts['port']

    logging.debug('About to open port %s' % port)
    s = SerialPort(Echo(), port, reactor, baudrate=baudrate)
    reactor.run()

"""run_tornado.py - Run a Flask app through the Tornado Python server"""

import signal
import logging
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
#from tornado.ioloop import IOLoop
import tornado.ioloop
from run import APP

IS_CLOSING = False
def signal_handler(signum, frame):
    """Define the server closing signal"""
    global IS_CLOSING
    logging.info('exiting...')
    IS_CLOSING = True
def try_exit():
    """Define the server exit function"""
    global IS_CLOSING
    if IS_CLOSING:
        # clean up here
        tornado.ioloop.IOLoop.instance().stop()
        logging.info('exit success')

SERVER = HTTPServer(WSGIContainer(APP))
signal.signal(signal.SIGINT, signal_handler)
SERVER.listen(5555)
tornado.ioloop.PeriodicCallback(try_exit, 100).start()
tornado.ioloop.IOLoop.instance().start()
#IOLoop.instance().start()

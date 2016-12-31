from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
#from tornado.ioloop import IOLoop
import tornado.ioloop
import signal
import logging
from run import app

is_closing = False
def signal_handler(signum, frame):
    global is_closing
    logging.info('exiting...')
    is_closing = True
def try_exit():
    global is_closing
    if is_closing:
        # clean up here
        tornado.ioloop.IOLoop.instance().stop()
        logging.info('exit success')

http_server = HTTPServer(WSGIContainer(app))
signal.signal(signal.SIGINT, signal_handler)
http_server.listen(5555)
tornado.ioloop.PeriodicCallback(try_exit, 100).start()
tornado.ioloop.IOLoop.instance().start()
#IOLoop.instance().start()

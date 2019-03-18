import tornado.ioloop
import tornado.web

import constants
from handlers import StartLoggingHandler


def make_server():
    return tornado.web.Application([
        (r"/startLogging/(.*)", StartLoggingHandler),
    ])


if __name__ == "__main__":
    server = make_server()
    server.listen(constants.DEFAULT_LOGGING_SERVER_PORT)
    tornado.ioloop.IOLoop.current().start()

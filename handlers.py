from typing import Optional, Awaitable, Generator
import threading

import tornado.web
import docker
from docker import DockerClient
from docker.errors import NotFound, APIError
from docker.models.containers import Container

from stream_logs import stream_logs_from_generator

DOCKER_CLIENT: DockerClient = docker.from_env()


class GeneralHTTPHandler(tornado.web.RequestHandler):
    def data_received(self, chunk: bytes) -> Optional[Awaitable[None]]:
        pass

    def options(self, *args):
        self.set_status(204)
        self.finish()


class StartLoggingHandler(GeneralHTTPHandler):
    def get(self, name: str):
        try:
            container: Container = DOCKER_CLIENT.containers.get(name)
            generator: Generator = container.logs(stream=True, timestamps=True)
            if len(list(filter(lambda t: t.name == name, threading.enumerate()))) == 0:
                threading.Thread(target=stream_logs_from_generator, args=(name, generator), name=name,
                                 daemon=True).start()
        except NotFound:
            pass
        except APIError:
            pass

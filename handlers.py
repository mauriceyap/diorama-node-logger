from typing import Optional, Awaitable, Generator
import threading
from datetime import datetime
from datetime import timedelta

import tornado.web
import docker
from docker import DockerClient
from docker.errors import NotFound, APIError
from docker.models.containers import Container

from stream_logs import stream_logs_from_generator

RFC_3339_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
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
            since_raw = self.get_argument("since", None)
            since = (datetime.strptime(since_raw[0:26] + since_raw[29], RFC_3339_FORMAT) + timedelta(
                milliseconds=1) if since_raw else None)
            container: Container = DOCKER_CLIENT.containers.get(name)
            generator: Generator = container.logs(stream=True, timestamps=True, since=since)
            if len(list(filter(lambda t: t.name == name, threading.enumerate()))) == 0:
                threading.Thread(target=stream_logs_from_generator, args=(name, generator, since_raw), name=name,
                                 daemon=True).start()
        except NotFound:
            pass
        except APIError:
            pass

from typing import Generator, List, Dict
from tornado.httpclient import HTTPClient, HTTPRequest
import json
import asyncio

import constants


def stream_logs_from_generator(name: str, generator: Generator, since_raw):
    asyncio.set_event_loop(asyncio.new_event_loop())
    http_client = HTTPClient()
    while True:
        try:
            line: bytes = generator.__next__()
            split_line: List[bytes] = line.split(b' ', maxsplit=1)
            timestamp = split_line[0].decode('utf-8')
            if since_raw and timestamp <= since_raw:
                continue
            to_send: Dict[str, str] = {
                'timestamp': timestamp,
                'message': split_line[1].decode('utf-8'),
                'nid': name
            }
            http_client.fetch(
                HTTPRequest(url=constants.MAIN_SERVER_LOGGING_MESSAGE_URL, method='POST', body=json.dumps(to_send)))
        except StopIteration:
            break

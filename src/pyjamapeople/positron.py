# coding: utf-8

# pylint: disable=missing-docstring
# pylint: disable=logging-format-interpolation
# pylint: disable=line-too-long
# pylint: disable=invalid-name
# pylint: disable=too-many-lines

import asyncio
import logging
import traceback
import json

import tornado.web            # pylint: disable=import-error
import tornado.httpserver     # pylint: disable=import-error
import tornado.ioloop         # pylint: disable=import-error
import tornado.websocket      # pylint: disable=import-error
import tornado.options        # pylint: disable=import-error
import tornado.escape


class HttpHandler(tornado.web.RequestHandler):  # pylint: disable=too-few-public-methods, abstract-method

    parent = None

    def initialize(self, *args, **kwargs):

        self.parent = kwargs.pop('parent')
        super().initialize(*args, **kwargs)

    def get(self):

        ctx = {
            "title": "Pyjama Peolple",
            "footer": "© Munchkin Music Co - https://www.zappa.com/",
        }
        ret = self.render("index.html", **ctx)
        return ret


class WebsockHandler(tornado.websocket.WebSocketHandler):  # pylint: disable=abstract-method

    parent = None

    def initialize(self, **kwargs):

        self.parent = kwargs.pop('parent')

    def open(self, *args, **kwargs):

        super().open(*args, **kwargs)

        self.parent.notify_ws_client(self, 'open')

    def on_message(self, message):

        self.parent.notify_ws_client(self, 'on_message', message)

    def on_close(self):

        self.parent.notify_ws_client(self, 'close')


class Positron:

    web_socket_channels = []
    tornado_instance = None

    def __init__(self, port: int, address: str, tornado_options: dict):

        self.tornado_options = tornado_options
        self.port = port
        self.address = address

        self.application_instance = None

    async def _handle_message_from_front(self, ws_socket, data):

        try:

            data = json.loads(data)

            _callable = data.get('callable')
            _args = data.get('args', {})
            logging.debug(f"data:{data}, _args:{_args}")

            if self.application_instance and hasattr(self.application_instance, _callable):
                ret = await getattr(self.application_instance, _callable)(ws_socket, **_args)
                if ret:
                    logging.warning(f"ret:{ret}")

        except Exception as e:  # pylint: disable=broad-except
            logging.error(traceback.format_exc())
            self.call_on_front(_callable='alert_message', args={'Exception': str(e)}, ws_socket=ws_socket)

    def call_on_front(self, _callable, args, ws_socket=None):

        msg = {'callable': _callable, 'args': args}
        msg = json.dumps(msg, ensure_ascii=False)

        try:

            # ~ if ws_socket and ws_socket in self.web_socket_channels:
            if ws_socket:
                t_ = ws_socket.write_message(msg)
                asyncio.ensure_future(t_)

            else:  # broadcast
                for ws_s in self.web_socket_channels:
                    t_ = ws_s.write_message(msg)
                    asyncio.ensure_future(t_)

        except tornado.websocket.WebSocketClosedError:

            logging.error(traceback.format_exc())

            if ws_socket in self.web_socket_channels:
                self.web_socket_channels.remove(ws_socket)

    def run(self):

        url_map = [
            (r"/", HttpHandler, {'parent': self}),
            (r'/websocket', WebsockHandler, {'parent': self}),
        ]

        self.tornado_instance = tornado.web.Application(url_map, **self.tornado_options)

        logging.warning("starting tornado webserver on http://{0}:{1}...".format(self.address, self.port))

        self.tornado_instance.listen(self.port, self.address)
        tornado.platform.asyncio.AsyncIOMainLoop().install()

    def notify_ws_client(self, ws_socket, event, message=None):

        if event == 'open':

            self.web_socket_channels.append(ws_socket)
            logging.info(f"n. of active web_socket_channels:{len(self.web_socket_channels)}")

            self.application_instance.handle_new_ws_client(ws_socket)

        elif event == 'close':

            self.web_socket_channels.remove(ws_socket)
            logging.info(f"n. of active web_socket_channels:{len(self.web_socket_channels)}")

        elif event == 'on_message':

            t_ = self._handle_message_from_front(ws_socket, message)
            asyncio.ensure_future(t_)

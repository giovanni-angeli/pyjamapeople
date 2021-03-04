# coding: utf-8

# pylint: disable=missing-docstring
# pylint: disable=logging-format-interpolation
# pylint: disable=line-too-long
# pylint: disable=invalid-name
# pylint: disable=too-many-lines

import sys
import os
import time
import asyncio
import logging
import traceback
import random

import tornado.web            # pylint: disable=import-error
import tornado.httpserver     # pylint: disable=import-error
import tornado.ioloop         # pylint: disable=import-error
import tornado.websocket      # pylint: disable=import-error
import tornado.options        # pylint: disable=import-error

HERE = os.path.dirname(os.path.abspath(__file__))

LISTEN_PORT = 8000
LISTEN_ADDRESS = '127.0.0.1'

APPLICATION_OPTIONS = dict(
    debug=True,
    autoreload=True,
    template_path=os.path.join(HERE, "..", "templates"),
    compiled_template_cache=False)

GLOBAL_APPLICATION_INSTANCE = None


async def wait_for_condition(
        condition,
        extra_info=None,
        silent=False,
        timeout=10,
        callback=None,
        stability_count=2,
        step=0.1):

    ret = None
    t0 = time.time()
    counter = 0
    try:
        while time.time() - t0 < timeout:

            if condition and condition():
                counter += 1
                if counter >= stability_count:
                    if callback:
                        callback()
                    ret = True
                    break
            else:
                counter = 0

            await asyncio.sleep(step)

        if not ret and not silent:

            _ = f"timeout expired! timeout:{timeout}.\n"
            if extra_info:
                _ += str(extra_info)

            logging.warning(_)

    except Exception:  # pylint: disable=broad-except
        logging.error(traceback.format_exc())

    return ret


def get_application_instance():

    global GLOBAL_APPLICATION_INSTANCE  # pylint: disable=global-statement

    if GLOBAL_APPLICATION_INSTANCE is None:
        GLOBAL_APPLICATION_INSTANCE = Application()

    return GLOBAL_APPLICATION_INSTANCE


class HttpHandler(tornado.web.RequestHandler):

    def get(self):

        ctx = {
            "title": "Po‐Jama People",
            "footer": "© Munchkin Music Co - https://www.zappa.com/",
        }
        ret = self.render("index.html", **ctx)
        return ret


class WebsockHandler(tornado.websocket.WebSocketHandler):

    def initialize(self):

        a = get_application_instance()
        a.web_socket_channels.append(self)

        logging.info(f"n. of active web_socket_channels:{len(a.web_socket_channels)}")

        self.msg_counter = 0

    def open(self, *args, **kwargs):

        super().open(args, kwargs)
        logging.info(f"")

    def on_message(self, message):

        logging.info(f"message:{message}")
        self.msg_counter += 1
        answ = {
            'time': time.asctime(),
            'js': 'document.getElementById("answer_target").innerHTML="{} [{}] {} -> {}";'.format(
                self.msg_counter, time.asctime(), message, content_producer()),
        }

        self.write_message(answ)

    def on_close(self):

        logging.info(f"")
        a = get_application_instance()
        a.web_socket_channels.remove(self)


class Heartbeat:

    async def run(self, task_id):

        while True:

            active_channels = get_application_instance().web_socket_channels
            n_of_active_channels = len(active_channels)
            logging.debug(f"n_of_active_channels:{n_of_active_channels}")

            for h in active_channels:
                try:
                    msg = {
                        'time': time.asctime(),
                        'js': 'document.getElementById("heartbeat_target").innerHTML="server time:{} (active channels:{})";'.format(
                            time.asctime(),
                            n_of_active_channels),
                    }

                    h.write_message(msg)

                    for i in range(1, 4):
                        for j in range(1, 6):
                            target_id = f"data_{i}_{j}"
                            stuff = await get_application_instance().get_stuff_from_resource(task_id)
                            msg = {
                                'time': time.asctime(),
                                'js': 'document.getElementById("{}").innerHTML="task_id:{} {}";'.format(
                                    target_id,
                                    task_id,
                                    stuff),
                            }
                            h.write_message(msg)

                except tornado.websocket.WebSocketClosedError:
                    pass

                except Exception:    # pylint: disable=broad-except
                    logging.error(traceback.format_exc())

            await asyncio.sleep(1)


class Application:

    url_map = [
        (r"/", HttpHandler, {}),
        (r'/websocket', WebsockHandler, {}),
    ]

    web_socket_channels = []
    who_is_locking = []
    waiting_tasks = []

    async def get_stuff_from_resource(self, task_id):

        def condition():
            return not self.who_is_locking

        ret = None

        self.waiting_tasks.append(task_id)
        r = await wait_for_condition(condition, silent=0, timeout=5, step=.001, extra_info=f"task_id:{task_id} ")
        self.waiting_tasks.remove(task_id)

        if r:
            self.who_is_locking.append(task_id)
            logging.debug(f" who_is_locking:{self.who_is_locking},".ljust(20) + f" waiting_tasks:{self.waiting_tasks}")
            assert len(self.who_is_locking) == 1
            assert self.who_is_locking not in self.waiting_tasks

            await asyncio.sleep(.001)
            ret = content_producer()
            await asyncio.sleep(.001)

            self.who_is_locking.remove(task_id)
            logging.debug(f" who_is_locking:{self.who_is_locking},".ljust(20) + f" waiting_tasks:{self.waiting_tasks}")
            assert len(self.who_is_locking) == 0

            await asyncio.sleep(.00001)

        return ret

    def start_tornado(self):

        logging.info("starting tornado webserver on {}:{}...".format(LISTEN_ADDRESS, LISTEN_PORT))

        app = tornado.web.Application(self.url_map, **APPLICATION_OPTIONS)
        app.listen(LISTEN_PORT, LISTEN_ADDRESS)
        tornado.platform.asyncio.AsyncIOMainLoop().install()

    def start_backend_task(self):

        logging.info("starting backend task...")

        for i in range(100):
            _future = Heartbeat().run(i)
            asyncio.ensure_future(_future)
            time.sleep(.01)

    def run(self):

        self.start_tornado()
        self.start_backend_task()

        asyncio.get_event_loop().run_forever()


def main():

    logging.basicConfig(
        stream=sys.stdout, level="INFO",
        format="[%(asctime)s]%(levelname)s %(funcName)s() %(filename)s:%(lineno)d %(message)s")

    a = get_application_instance()
    a.run()


def content_producer():
    """
Fonte: Musixmatch
Compositori: Zappa F
Testo di Po‐Jama People © Munchkin Music Co
    """

    _ = """
Some people's hot
Some people's cold
Some people's not very
Swift to behold
Some people do it
Some see right through it
Some wear pyjamas
If only they knew it
The pyjama people are boring me to pieces
Feel like I am wasting my time
They all got flannel up 'n down 'em
A little trap-door back aroun' 'em
An' some cozy little footies on their mind
Po-jama people!
Po-jama people, people!
They sure do make you sleepy
With the things they might say
Po-jama people!
Po-jama people, people!
Mother Mary 'n Jozuf, I wish they'd all go away!
Po-jama people!
It's a po-jama people special . . .
Take one home with you, save a dollar today
Po-jama people!
Po-jama people, people!
Wrap 'em up
Roll 'em out
Get 'em out of my way
Hein nya-nya-hein nya-nya-hein nya-nya-hein
HOEY! HOEY! HOEY!
Wrap 'em up
Roll 'em out
Get 'em out of my way
Hein nya-nya-hein nya-nya-hein nya-nya-hein
HOEY! HOEY! HOEY!
Wrap 'em up
Roll 'em out
Get 'em out of my way
Hein nya-nya-hein nya-nya-hein nya-nya-hein
HOEY! HOEY! HOEY!
now some people's hot
An' some people's cold
(Well, Lawd . . .) an' some people's not very
(Very) swift to behold (swifty!)
(I told you) some people do it (do it!)
(Yes, they do!) (No . . .)
Some see right through it
(See right through it!)
An' some wear PO-JAMAS
If only they knew it
The pyjama people are boring me to pieces
They make me feel like I am wasting my time
They all got flannel up 'n down 'em
A little trap-door back aroun' 'em
An' some cozy little footies on their mind
Po-jama people!
Po-jama people, people!
Lawd, they make you sleepy
With the things they might say (hey, yeah-hey . . .)
Po-jama people!
(Well . . . now) Po-jama people, people!
(I said) ARF! ARF! ARF!
I wish they'd all go away!
Po-jama people! (People!) (Oh, yeah)
Po-jama people special . . .
(I said, I said, I said)
Take one home with you, & save a dollar today
Po-jama people!
(It's a) Po-jama people, people! (Special)
Wrap 'em up
An' roll 'em out
Get 'em out of my way
HOEY! HOEY! HOEY!
Wrap 'em up
An' roll 'em out
Get 'em out of my way
HOEY! HOEY! HOEY!
Wrap 'em up
Roll 'em out
Get 'em out of my way
HOEY! HOEY! HOEY!
"""

    return random.choice([t for t in _.split('\n') if t])


if __name__ == '__main__':
    main()

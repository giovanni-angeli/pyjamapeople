# coding: utf-8

# pylint: disable=missing-docstring
# pylint: disable=logging-format-interpolation
# pylint: disable=line-too-long
# pylint: disable=invalid-name
# pylint: disable=too-many-lines

import time
import asyncio
import logging
import traceback


class Application:  # pylint: disable=too-few-public-methods

    running = False

    def __init__(self, options):

        self.options = options
        self.positron_instance = None

    async def _a_run(self):

        logging.info(f"START")

        t0 = time.time()

        while self.running:

            try:
                if self.positron_instance:

                    self.positron_instance.call_on_front(
                        _callable='set_innerHTML',
                        args={'innerHTML': time.asctime(), 'element_id': 'time_display'})

                    # ~ bgcol = ["#FFEEEE", "#EEFFFF", "#FFFFEE"][int(time.time()) % 3]
                    # ~ bgcol = "#{0:02X}{0:02X}{0:02X}".format(150 + int(10*time.time()) % 105)
                    bgcol = "#FFFF{0:02X}".format(155 + int(20*(time.time() - t0)) % 100)
                    self.positron_instance.call_on_front(
                        _callable='set_attribute',
                        args={'name': 'style', 'value': f'background-color: {bgcol};', 'element_id': 'time_display'})

            except Exception:    # pylint: disable=broad-except
                logging.error(traceback.format_exc())
                await asyncio.sleep(5)

            await asyncio.sleep(1)

        logging.info(f"EXIT")

    def run(self):

        if not self.running:
            self.running = True
            asyncio.ensure_future(self._a_run())

    async def log_from_front(self, ws_sock, value=None):

        logging.warning(f"{value}")

    async def one(self, ws_sock, value=None):

        self.positron_instance.call_on_front(
            _callable='alert_message', args=f'you called one() with value:{value}')

    async def two(self, ws_sock, value=None):

        self.positron_instance.call_on_front(
            _callable='alert_message', args=f'you called two() with value:{value}')

    async def three(self, ws_sock, value=None):

        self.positron_instance.call_on_front(
            _callable='alert_message', args= {'you called three()': f'value:{value}'})

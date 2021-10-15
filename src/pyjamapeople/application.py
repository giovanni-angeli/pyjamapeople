# coding: utf-8

# pylint: disable=missing-docstring
# pylint: disable=logging-format-interpolation
# pylint: disable=line-too-long
# pylint: disable=invalid-name
# pylint: disable=too-many-lines

import os
import time
import asyncio
import logging
import traceback
import inspect
import random
import codecs

from tornado import template as tornado_template


class TimeDisplayWidget:

    def __init__(self, parent):

        self.parent = parent
        self.element_id = 'time_display'
        self.t0 = time.time()

    def render(self):

        bgcol = "#FFFF{0:02X}".format(155 + int(20 * (time.time() - self.t0)) % 100)

        _html = """
        <label style="background-color:{0};">backend time:{1}</label>
        """.format(bgcol, time.asctime())

        return _html

    def show(self, ws_socket=None):

        html_ = self.render()

        if self.parent and self.parent.positron_instance:
            self.parent.positron_instance.call_on_front(
                _callable='set_innerHTML',
                args={'innerHTML': html_, 'element_id': self.element_id},
                ws_socket=ws_socket)


class ImageListWidget:

    def __init__(self, parent):

        self.parent = parent
        self.element_id = 'img_container'

        _here = os.path.dirname(os.path.abspath(__file__))
        self.img_list = os.listdir(os.path.join(_here, '..', 'static', 'img'))

    def render(self):

        random.shuffle(self.img_list)

        _html = ''
        for img in self.img_list:
            _html += """<img style="height:400px;margin:4px;" src="/static/img/{}" alt="not found"></img>
            """.format(img)

        return _html

    def show(self, ws_socket):

        html_ = self.render()

        if self.parent and self.parent.positron_instance:
            self.parent.positron_instance.call_on_front(
                _callable='set_innerHTML',
                args={'innerHTML': html_, 'element_id': self.element_id},
                ws_socket=ws_socket)


class CallableListWidget:

    def __init__(self, parent):

        self.parent = parent

        self.element_id = 'exported_callables_from_py_to_js_container'

        self._template = tornado_template.Template("""utf-8 인코딩의 문자열을 허용합니다.
            <input type="submit" id="{{name}}" value="{{name}}"
                onclick="_btn_call_on_backend('{{name}}');"/>
            <input type="text" id="{{name}}_args" placeholder="value"
                onkeypress="if (window.event.which == 13) {_btn_call_on_backend('{{name}}');};"/>
            <br/>
            <label>{{description}}</label>
            <label> </label>
            <hr></hr>""")

    def render(self):
        """ this is black magic, beware. """

        def _filter(name, _callable):
            return not name.startswith("_") and asyncio.iscoroutinefunction(_callable)

        _list = []
        for name in dir(self.parent):
            _funct = getattr(self.parent, name)
            if _filter(name, _funct):
                description = inspect.getdoc(_funct)
                _list.append(dict(name=name, description=description))

        _list.sort(key=lambda x: x.get("description"))
        _list = [self._template.generate(**_) for _ in _list]
        _html = "".join([codecs.decode(i, 'utf-8') for i in _list])

        return _html

    def show(self, ws_socket):

        html_ = self.render()

        if self.parent and self.parent.positron_instance:
            self.parent.positron_instance.call_on_front(
                _callable='set_innerHTML',
                args={'innerHTML': html_, 'element_id': self.element_id},
                ws_socket=ws_socket)


class Application:

    running = False

    def __init__(self, options):

        self.options = options
        self.positron_instance = None

    def handle_new_ws_client(self, ws_socket):

        CallableListWidget(self).show(ws_socket)

    async def _a_run(self):

        logging.info(f"START")

        time_display_widget = TimeDisplayWidget(self)

        while self.running:

            try:

                time_display_widget.show()

            except Exception:    # pylint: disable=broad-except
                logging.error(traceback.format_exc())
                await asyncio.sleep(5)

            await asyncio.sleep(1)

        logging.info(f"EXIT")

    def stop(self):

        ret = False
        if self.running:
            self.running = False
            ret = True

        return ret

    def run(self):

        ret = False
        if not self.running:
            self.running = True
            asyncio.ensure_future(self._a_run())
            ret = True

        return ret

    async def start_from_js(self, ws_socket, **args):

        """1 start the backend's main task (if stoppped)

        No input is used. """

        if self.run():
            self.positron_instance.call_on_front(
                _callable='alert_message',
                args=f'you started main task',
                ws_socket=ws_socket)

    async def stop_from_js(self, ws_socket, **args):

        """2 stop the backend's main task (if started)

        No input is used. """

        if self.stop():
            self.positron_instance.call_on_front(
                _callable='alert_message',
                args=f'you stopped main task',
                ws_socket=ws_socket)

    async def alert_from_py_to_js(self, ws_socket, **args):

        """3 make the backend popping up an alert message in browser UI """

        self.positron_instance.call_on_front(
            _callable='alert_message',
            args=f'you called alert_from_py_to_js() with args:{args}',
            ws_socket=ws_socket)

    async def log_from_js_to_py(self, ws_socket, **args):

        """4 output a message via the python logging system in the backend (level: WARNING).

        Input args are logged as string.
        Check python process' stdout.

        """

        logging.warning(f"args:{args} from:{ws_socket}")

    async def show_images(self, ws_socket, value=10):

        """5 make the backend show shuffled images in browser UI.
        input value (float) is used as duration in sec. """

        duration = float(value)

        image_list_widget = ImageListWidget(self)

        t0 = time.time()
        while time.time() - t0 < duration:

            image_list_widget.show(ws_socket)

            await asyncio.sleep(.2)

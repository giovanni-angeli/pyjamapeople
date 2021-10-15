# coding: utf-8

# pylint: disable=missing-docstring
# pylint: disable=logging-format-interpolation
# pylint: disable=invalid-name

import sys
import os
import logging
import traceback
import asyncio

from pyjamapeople.positron import Positron
from pyjamapeople.application import Application

HERE = os.path.dirname(os.path.abspath(__file__))

APPLICATION_OPTIONS = dict()

POSITRON_OPTIONS = dict(
    debug=True,
    autoreload=True,
    template_path=os.path.join(HERE, '..', 'template'),
    static_path=os.path.join(HERE, '..', 'static'),
    compiled_template_cache=False)

def main():

    logging.basicConfig(
        stream=sys.stdout,
        level="INFO",
        format="[%(asctime)s]%(levelname)s %(funcName)s() %(filename)s:%(lineno)d %(message)s")

    a = Application(APPLICATION_OPTIONS)
    p = Positron(port=8000, address='127.0.0.1', tornado_options=POSITRON_OPTIONS)

    p.application_instance = a
    a.positron_instance = p

    p.run()
    a.run()

    try:
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        pass
    except Exception:  # pylint: disable=broad-except
        logging.error(traceback.format_exc())
    finally:
        asyncio.get_event_loop().stop()
        asyncio.get_event_loop().run_until_complete(
            asyncio.get_event_loop().shutdown_asyncgens())
        asyncio.get_event_loop().close()


if __name__ == '__main__':
    main()

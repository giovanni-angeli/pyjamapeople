# Pyjamapeolple

a simple but fully featured example of how to use **tornado**, **asyncio** and **websocket** together 
to build an application delagating the frontend UI to a browser, local or remote,
without the limits of the http dialogs.

TAGS: tornado asyncio websocket 

3. create a virtualenv 
>     $ export VIRTEN_VROOT=desired-virtenv_root-path
>     $ mkdir ${VIRTEN_VROOT}
>     $ virtualenv -p /usr/bin/python3 ${VIRTEN_VROOT}

2. clone this project in ${PROJECT_ROOT}
>     $ export PROJECT_ROOT=<desired-project_root-path>

1. build Install in edit mode:
>     $ cd ${PROJECT_ROOT}               
>     $ . ${VIRTEN_VROOT}/bin/activate
>     $ pip install -e ./

4. Run:
>     $ (. ${VIRTEN_VROOT}/bin/activate ; pyjamapeolple &)
>     $ chromium http://127.0.0.1:8000/ &
>     $ firefox http://127.0.0.1:8000/ &



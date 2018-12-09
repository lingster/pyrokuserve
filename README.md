# pyrokuserve
[Sanic](https://github.com/huge-success/sanic) based web server to control your home roku device, based on the api: [python-roku](https://github.com/jcarbaugh/python-roku).

## Setup
use pipenv to install dependencies:
```bash
pipenv install
```
then  either 
```bash
pipenv run pyrokuserve.py
```
or 
```bash
pipenv shell
python pyrokuserve.py
```

This will startup the sanic web server on default port 8000. 

you can then send rest requests like:

|URL|Description|
|---|-----------|
|http://localhost:8000/device/list/  | returns list of roku devices |
|http://localhost:8000/device/<device_id>/apps/list/ | specify the roku device(from the previous call) and this will return you list of available channels on that device|
|http://localhost:8000/device/<device_id>/commandlist/ | returns list of commands to run against the device |
|http://localhost:8000/device/1/command/<command>/ | execute the command, eg home will send roku to the home page |

There are some very simple pytests in here.


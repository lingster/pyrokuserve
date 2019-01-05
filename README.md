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

Swagger documentation is available here: 
http://localhost:8000/swagger

There are some very simple pytests in here.


Notes: 
Firewalld - if you are using firewalld, then you will need to open up traffic for incoming requests to port 1900 as well as outgoing requests. Following example services to be opened up: 

upnp-client.xml
<?xml version="1.0" encoding="utf-8"?>
<service>
  <short>UPnP Client</short>
  <description>Universal Plug and Play client for auto-configuration of network routers (use only in trusted zones).</description>
  <source-port port="1900" protocol="udp"/>
</service>

upnp.xml
<?xml version="1.0" encoding="utf-8"?>
<service>
  <short>UPNP</short>
  <description>Simple Service Discovery Protocol</description>
  <port protocol="udp" port="1900"/>
  <destination ipv4="239.255.255.250" ipv6="ff02::c" />
</service>

See: https://github.com/firewalld/firewalld/issues/25
and 
https://github.com/firewalld/firewalld/issues/260


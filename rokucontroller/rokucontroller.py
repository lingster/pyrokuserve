from roku import Roku

import log
import logging

log.setup_logging()
logger = logging.getLogger(__name__)


class RokuController():
    devices = []

    def __init__(self, timeout: int = 10):
        logger.info("Searching for roku devices...")
        self.devices = Roku.discover(timeout=timeout)
        if self.devices is None:
            logger.error("unable to find roku device")
            exit(-1)

        # mydevice = None
        # for d in self.devices:
        #    if d.port == 8060:
        #        print(f"controlling {d}")
        #        mydevice = d
        #        break

        if self.devices is None or len(self.devices) == 0:
            logger.error("unable to find roku on network")
            exit(-1)
        logger.info(f'Found {len(self.devices)} roku devices')
        # prime = self.get_app(mydevice, 'Amazon Prime Video')

    def get_devices(self):
        items = []
        for device in list(enumerate(self.devices)):
            item = {'id': device[0]}
            item['port'] = device[1].port
            item['host'] = device[1].host
            items.append(item)
        return items

    def exec_command(self, id: int, command: str):
        command_to_call = getattr(self.devices[id], command)
        command_to_call()
        return f'{command} executed'

    def get_apps(self, device_id: int):
        apps = {}
        logger.info(f'getting apps for device:{device_id}')
        for app in list(enumerate(self.devices[device_id])):
            apps[app[0]] = app[1].name
            logger.info(f'added: {app[1].name}')
        return apps

    def get_app(self, myroku: Roku, app_name: str):
        for app in myroku.apps:
            if app.name.to == app_name.lower():
                return app
        return None

    def launch_app(self, device_id: int, app_id: int):
        self.devices[device_id].apps[app_id].launch
        return {'status': 'ok'}

    def active_app(self, device_id: int):
        return self.devices[device_id].activeapp.name

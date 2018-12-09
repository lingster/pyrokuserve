from roku import Roku

import log
import logging

log.setup_logging()
logger = logging.getLogger(__name__)


class RokuController:
    devices = []

    def __init__(self, timeout: int = 5):
        logger.info("Searching for roku devices...")
        self.devices = Roku.discover(timeout=timeout)
        if self.devices is None:
            logger.error("unable to find roku device")
            exit(-1)

        if self.devices is None or len(self.devices) == 0:
            logger.error("unable to find roku on network")
            exit(-1)
        logger.info(f'Found {len(self.devices)} roku devices')
        # prime = self.get_app(mydevice, 'Amazon Prime Video')

    def get_devices(self):
        items = []
        for device in list(enumerate(self.devices)):
            item = {'id': device[0], 'port': device[1].port, 'host': device[1].host}
            items.append(item)
        return items

    def get_commands(self, device_id: int):
        return self.devices[device_id].commands

    def exec_command(self, device_id: int, command: str):
        command_to_call = getattr(self.devices[device_id], command)
        command_to_call()
        return f'{command} executed'

    def get_apps(self, device_id: int):
        apps = {}
        logger.info(f'getting apps for device:{device_id}')
        for app in self.devices[device_id].apps:
            apps[app.id] = {'name': app.name, 'version': app.version}
            logger.info(f'added: {app.id}, {app.name} / {app.version}')
        return apps

    def launch_app(self, device_id: int, app_id: int):
        return self.devices[device_id].apps[app_id].launch()

    def store_app(self, device_id: int, app_id: int):
        return self.devices[device_id].apps[app_id].store()

    def active_app(self, device_id: int):
        return self.devices[device_id].activeapp.name

    def literal(self, device_id: int, text: str):
        return self.devices[device_id].literal(text)

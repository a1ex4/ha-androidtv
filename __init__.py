from adb.client import Client as AdbClient
import re

BLOCK_PATTERN = 'STREAM_MUSIC(.*?)- STREAM'
DEVICE_PATTERN = 'Devices: (.*?)\W'
MUTED_PATTERN = 'Muted: (.*?)\W'
VOLUME_PATTERN = '\): (\d{1,})'

class ADBClient:
    
    def __init__(self):
        self._client = AdbClient(host="127.0.0.1", port=5037)

    def server_is_connected(self):
        """ Check if we can connect to the ADB server. """

        try:
            self._adb_devices = self._client.devices()
            return True

        except RuntimeError:
            return False

    def device_is_connected(self, host):
        """ Check if the ADB server is connected to the device. """
        try:
            if any([host in dev.get_serial_no() for dev in self._adb_devices]):
                return True
            else:
                return False
        except RuntimeError:
            return False
        

class Android:
    """ Represents an Android TV device. """

    def __init__(self, host, client, adb_device):
        """ Initialize AndroidTV object.
        :param host: Host in format <address>:port.
        :param apps: Custom user known apps
        :param client: ADB client object
        :param adb_device: ADB device object
        """
        self._client = client
        self._adb_device = adb_device
        self._host = host
        self._available = None
        self._volume = 0.
        self._muted = None
        self._state = None
        self._app_id = None
        self._device = None

        self.update()

    def update(self):
        # State detection
        power_output = self.shell('dumpsys power')
        audio_output = self.shell('dumpsys audio')

        if 'Display Power: state=ON' not in power_output:
            self._state = 'off'
        elif 'started' in audio_output:
            self._state = 'play'
        elif 'paused' in audio_output:
            self._state = 'pause'
        else:
            self._state = 'idle'

        # Audio
        stream_block = re.findall(
            BLOCK_PATTERN, audio_output, re.DOTALL | re.MULTILINE)[0]
        self._device = re.findall(DEVICE_PATTERN, stream_block,
                            re.DOTALL | re.MULTILINE)[0]
        muted = re.findall(MUTED_PATTERN, stream_block,
                           re.DOTALL | re.MULTILINE)[0]
        volume_level = re.findall(
            self._device + VOLUME_PATTERN, stream_block, re.DOTALL | re.MULTILINE)[0]
        
        if muted == 'true':
            self._muted = True
        else:
            self._muted = False

        self._volume = round(1/15 * int(volume_level), 2)

        # App ID
        self._app_id = self.current_app()


    def current_app(self):
        win_output = self.shell('dumpsys window windows')
        for line in win_output.splitlines():
            if 'mCurrentFocus' in line:
                current_app = line.split(' ')[4].split('/')[0]
                return current_app
        return None

    def shell(self, command):
        """ Execute a shell command on the device"""
        return(self. _adb_device.shell(command))

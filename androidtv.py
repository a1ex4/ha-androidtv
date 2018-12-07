"""
Provide functionality to interact with AndroidTv devices on the network.

Example config:
media_player:
  - platform: androidtv
    host: 192.168.1.37
    name: MIBOX3 ANDROID TV


For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/media_player.androidtv/
"""

import logging
import voluptuous as vol

from homeassistant.components.media_player import (
    DOMAIN, MediaPlayerDevice, PLATFORM_SCHEMA, SUPPORT_NEXT_TRACK,
    SUPPORT_PAUSE, SUPPORT_PLAY,
    SUPPORT_PREVIOUS_TRACK, SUPPORT_STOP, SUPPORT_TURN_OFF,
    SUPPORT_TURN_ON, SUPPORT_VOLUME_MUTE, SUPPORT_VOLUME_STEP)

from homeassistant.const import (
    ATTR_ENTITY_ID, CONF_HOST, CONF_NAME, CONF_PORT,
    STATE_IDLE, STATE_PAUSED, STATE_PLAYING, STATE_OFF)
from homeassistant.exceptions import PlatformNotReady
import homeassistant.helpers.config_validation as cv

REQUIREMENTS = ['pure-python-adb==0.1.5.dev0', 'androidtv']

_LOGGER = logging.getLogger(__name__)

CONF_APPS = 'apps'
DEFAULT_APPS = {}
DEFAULT_NAME = 'Android'
DEFAULT_PORT = '5555'

ACTIONS = {
    "back": "4",
    "blue": "186",
    "component1": "249",
    "component2": "250",
    "composite1": "247",
    "composite2": "248",
    "down": "20",
    "end": "123",
    "enter": "66",
    "green": "184",
    "hdmi1": "243",
    "hdmi2": "244",
    "hdmi3": "245",
    "hdmi4": "246",
    "home": "3",
    "input": "178",
    "left": "21",
    "menu": "82",
    "move_home": "122",
    "mute": "164",
    "pairing": "225",
    "power": "26",
    "resume": "224",
    "right": "22",
    "sat": "237",
    "search": "84",
    "settings": "176",
    "sleep": "223",
    "suspend": "276",
    "sysdown": "281",
    "sysleft": "282",
    "sysright": "283",
    "sysup": "280",
    "text": "233",
    "top": "122",
    "up": "19",
    "vga": "251",
    "voldown": "25",
    "volup": "24",
    "yellow": "185"
}

KNOWN_APPS = {
    "amazon": "Amazon Prime Video",
    "dream": "Screensaver",
    "kodi": "Kodi",
    "netflix": "Netflix",
    "plex": "Plex",
    "spotify": "Spotify",
    "tvlauncher": "Homescreen",
    "youtube": "Youtube",
    "zatto": "Zattoo"
}

SUPPORT_ANDROIDTV = (SUPPORT_NEXT_TRACK | SUPPORT_PAUSE |
                     SUPPORT_PLAY | SUPPORT_PREVIOUS_TRACK |
                     SUPPORT_TURN_OFF | SUPPORT_TURN_ON |
                     SUPPORT_VOLUME_MUTE | SUPPORT_VOLUME_STEP |
                     SUPPORT_STOP)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_PORT, default=DEFAULT_PORT): vol.All(cv.port, cv.string),
    vol.Optional(CONF_APPS, default=DEFAULT_APPS): dict,
})

ACTION_SERVICE = 'androidtv_action'
INTENT_SERVICE = 'androidtv_intent'
KEY_SERVICE = 'androidtv_key'

SERVICE_ACTION_SCHEMA = vol.Schema({
    vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
    vol.Required('action'): vol.In(ACTIONS),
})

SERVICE_INTENT_SCHEMA = vol.Schema({
    vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
    vol.Required('intent'): cv.string,
})

SERVICE_KEY_SCHEMA = vol.Schema({
    vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
    vol.Required('key'): cv.string,
})

DATA_KEY = '{}.androidtv'.format(DOMAIN)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the androidtv platform."""
    from androidtv import ADBClient
    if DATA_KEY not in hass.data:
        hass.data[DATA_KEY] = {}

    adb_client = ADBClient()

    ip = config.get(CONF_HOST)
    name = config.get(CONF_NAME)
    port = config.get(CONF_PORT)
    apps = config.get(CONF_APPS)
    host = "{}:{}".format(ip, port)

    if adb_client.server_is_connected():
        if adb_client.device_is_connected(host):
            adb_device = adb_client._client.device(host)
            androidtv = AndroidTvDevice(
                name, host, apps, adb_client, adb_device)
            add_entities([androidtv])
            if host in hass.data[DATA_KEY]:
                _LOGGER.warning(
                    "Platform already setup on {}, skipping.".format(host))
            else:
                hass.data[DATA_KEY][host] = androidtv
        else:
            _LOGGER.error(
                "ADB server not connected to {}".format(name))
            raise PlatformNotReady
    else:
        _LOGGER.error(
            "Can't reach adb server, is it running ?")
        raise PlatformNotReady

    def service_action(service):
        """Dispatch service calls to target entities."""
        params = {key: value for key, value in service.data.items()
                  if key != ATTR_ENTITY_ID}

        entity_id = service.data.get(ATTR_ENTITY_ID)
        target_devices = [dev for dev in hass.data[DATA_KEY].values()
                          if dev.entity_id in entity_id]

        for target_device in target_devices:
            target_device.do_action(params['action'])

    def service_intent(service):
        """Dispatch service calls to target entities."""
        params = {key: value for key, value in service.data.items()
                  if key != ATTR_ENTITY_ID}

        entity_id = service.data.get(ATTR_ENTITY_ID)
        target_devices = [dev for dev in hass.data[DATA_KEY].values()
                          if dev.entity_id in entity_id]

        for target_device in target_devices:
            target_device.start_intent(params['intent'])

    def service_key(service):
        """Dispatch service calls to target entities."""
        params = {key: value for key, value in service.data.items()
                  if key != ATTR_ENTITY_ID}

        entity_id = service.data.get(ATTR_ENTITY_ID)
        target_devices = [dev for dev in hass.data[DATA_KEY].values()
                          if dev.entity_id in entity_id]

        for target_device in target_devices:
            target_device.input_key(params['key'])

    hass.services.register(
        DOMAIN, ACTION_SERVICE, service_action, schema=SERVICE_ACTION_SCHEMA)
    hass.services.register(
        DOMAIN, INTENT_SERVICE, service_intent, schema=SERVICE_INTENT_SCHEMA)
    hass.services.register(
        DOMAIN, KEY_SERVICE, service_key, schema=SERVICE_KEY_SCHEMA)


class AndroidTvDevice(MediaPlayerDevice):
    """Representation of an Android TV device."""

    def __init__(self, name, host, apps, client, adb_device):
        from androidtv import Android
        self._androidtv = Android(host, client, adb_device)
        self._client = client
        self._host = host
        self._name = name
        self._apps = KNOWN_APPS
        self._apps.update(dict(apps))
        self._app_name = None
        self._state = None

    def update(self):
        if self._client.server_is_connected():
            if self._client.device_is_connected(self._host):
                self._androidtv.update()
                self._app_name = self.get_app_name(self._androidtv._app_id)

                if self._androidtv._state == 'off':
                    self._state = STATE_OFF
                elif self._androidtv._state == 'idle':
                    self._state = STATE_IDLE
                elif self._androidtv._state == 'play':
                    self._state = STATE_PLAYING
                elif self._androidtv._state == 'pause':
                    self._state = STATE_PAUSED

                # available
                if not self._androidtv._available:
                    self._androidtv._available = True
                    _LOGGER.info("Device {} connected.".format(self._name))

            else:
                # Device not connected
                if self._androidtv._available:
                    self._androidtv._available = False
                    _LOGGER.error(
                        "ADB server not connected to {}".format(self._name))
                    _LOGGER.warning(
                        "Device {} became unavailable.".format(self._name))

        else:
            # can't reach server
            if self._androidtv._available:
                self._androidtv._available = False
                _LOGGER.error(
                    "Can't reach adb server, is it running ?")
                _LOGGER.warning(
                    "Device {} became unavailable.".format(self._name))

    def get_app_name(self, app_id):
        """Return the app name from its id and known apps."""
        i = 0
        for app in self._apps:
            if app in app_id:
                app_name = self._apps[app]
                i += 1
        if i == 0:
            app_name = None

        return app_name

    @property
    def name(self):
        """Return the name of the device."""
        return self._name

    @property
    def state(self):
        """Return the state of the device."""
        return self._state

    @property
    def is_volume_muted(self):
        """Boolean if volume is currently muted."""
        return self._androidtv._muted

    @property
    def volume_level(self):
        """Return the volume level."""
        return self._androidtv._volume

    @property
    def source(self):
        """Return the current playback device."""
        return self._androidtv._device

    @property
    def app_id(self):
        """ID of the current running app."""
        return self._androidtv._app_id

    @property
    def app_name(self):
        """Name of the current running app."""
        return self._app_name

    @property
    def available(self):
        """Return True if entity is available."""
        return self._androidtv._available

    @property
    def supported_features(self):
        """Flag media player features that are supported."""
        return SUPPORT_ANDROIDTV

    def turn_on(self):
        """Instruct the tv to turn on."""
        self._adb_device.shell('input keyevent 26')

    def turn_off(self):
        """Instruct the tv to turn off."""
        self._adb_device.shell('input keyevent 26')

    def media_play(self):
        """Send play command."""
        self._adb_device.shell('input keyevent 126')
        self._state = STATE_PLAYING

    def media_pause(self):
        """Send pause command."""
        self._adb_device.shell('input keyevent 127')
        self._state = STATE_PAUSED

    def media_play_pause(self):
        """Send play/pause command."""
        self._adb_device.shell('input keyevent 85')

    def media_stop(self):
        """Send stop command."""
        self._adb_device.shell('input keyevent 86')
        self._state = STATE_IDLE

    def mute_volume(self, mute):
        """Mute the volume."""
        self._adb_device.shell('input keyevent 164')
        self._muted = mute

    def volume_up(self):
        """Increment the volume level."""
        self._adb_device.shell('input keyevent 24')

    def volume_down(self):
        """Decrement the volume level."""
        self._adb_device.shell('input keyevent 25')

    def media_previous_track(self):
        """Send previous track command."""
        self._adb_device.shell('input keyevent 88')

    def media_next_track(self):
        """Send next track command."""
        self._adb_device.shell('input keyevent 87')

    def input_key(self, key):
        """Input the key to the device."""
        self._adb_device.shell("input keyevent {}".format(key))

    def start_intent(self, uri):
        """Start an intent on the device."""
        self._adb_device.shell(
            "am start -a android.intent.action.VIEW -d {}".format(uri))

    def do_action(self, action):
        """Input the key corresponding to the action."""
        self._adb_device.shell("input keyevent {}".format(ACTIONS[action]))

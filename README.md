# media_player-androidtv


## 0. Checklist for creating a platform

### 0.0 Common

 1. Follow our [Style guidelines](development_guidelines.md)
- [x] Use existing constants from [`const.py`](https://github.com/home-assistant/home-assistant/blob/dev/homeassistant/const.py)

### 0.1 Requirements

- [x] [HERE](https://github.com/a1ex4/home-assistant/blob/androidtv/homeassistant/components/media_player/androidtv.py#L35) Requirement version should be pinned: `REQUIREMENTS = ['phue==0.8.1']` 
- [x] We no longer want requirements hosted on GitHub. Please upload to PyPi.
- [x] Requirements should only be imported inside functions. This is necessary because requirements are installed on the fly.

### 0.2 Dependencies

- [x] If you depend on a component for the connection, add it to your dependencies: `DEPENDENCIES = ['nest']`

### 0.3 Configuration

- [x] [HERE](https://github.com/a1ex4/home-assistant/blob/androidtv/homeassistant/components/media_player/androidtv.py#L50-L57) Voluptuous schema present for [configuration validation](development_validation.md) 
- [ ] (not sure?) Voluptuous schema extends schema from component<br>(e.g., `light.hue.PLATFORM_SCHEMA` extends `light.PLATFORM_SCHEMA`)
- [x] Default parameters specified in voluptuous schema, not in `setup_platform(...)`
- [x] Your `PLATFORM_SCHEMA` should use as many generic config keys as possible from `homeassistant.const`

- [x] Never depend on users adding things to `customize` to configure behavior inside your platform.

### 0.4 Setup Platform

- [x] Test if passed in info (user/pass/host etc.) works.
- [x] [HERE](https://github.com/a1ex4/home-assistant/blob/androidtv/homeassistant/components/media_player/androidtv.py#L150) Group your calls to `add_devices` if possible. 
- [x] If platform adds extra services, format should be `<component>.<platform>_<service name>`. [here](https://github.com/a1ex4/home-assistant/blob/androidtv/homeassistant/components/media_player/androidtv.py#L173)

### 0.5 Entity
[HERE](https://github.com/a1ex4/home-assistant/blob/androidtv/homeassistant/components/media_player/androidtv.py#L176)
- [x] Extend entity from component, e.g., `class HueLight(Light)`.
- [x] Avoid passing in `hass` as a parameter to the entity. When the entity has been added to Home Assistant, `hass` will be set on the entity by the helper in entity_platform.py. This means you can access `hass` as `self.hass` inside the entity.
- [x] Do not call `update()` in constructor, use `add_entities(devices, True)` instead.
- [x] Do not do any I/O inside properties. Cache values inside `update()` instead.
- [x] The state and/or attributes should not contain relative time since something happened. Instead it should store UTC timestamps.

### 0.6 Communication with devices/services

- [x] All API specific code has to be part of a third party library hosted on PyPi. Home Assistant should only interact with objects and not make direct calls to the API.

## Silver 🥈

This integration is able to cope when things go wrong. It will not print any exceptions nor will it fill the log with retry attempts.

- [x] [HERE](https://github.com/a1ex4/home-assistant/blob/androidtv/homeassistant/components/media_player/androidtv.py#L202)Set an appropriate `SCAN_INTERVAL` (if a polling integration) 
- [x] [HERE](https://github.com/a1ex4/home-assistant/blob/androidtv/homeassistant/components/media_player/androidtv.py#L115-L148) Raise `PlatformNotReady` if unable to connect during platform setup (if appropriate) 
- [x] (no auth) Handles expiration of auth credentials. Refresh if possible or print correct error and fail setup. If based on a config entry, should trigger a new config entry flow to re-authorize.
- [x] (no internet access needed) Handles internet unavailable. Log a warning once when unavailable, log once when reconnected.
- [x] Handles device/service unavailable. Log a warning once when unavailable, log once when reconnected.
- [x] Set `available` property to `False` if appropriate ([docs](entity_index.md#generic-properties))
- [ ] Entities have unique ID (if available) ([docs](entity_registry_index.md#unique-id-requirements))

## Gold 🥇

This is a solid integration that is able to survive poor conditions and can be configured via the user interface.

- [ ] Configurable via config entries.
  - Don't allow configuring already configured device/service (example: no 2 entries for same hub)
  - Tests for the config flow
  - Discoverable (if available)
- [ ] Entities have device info (if available) ([docs](device_registry_index.md#defining-devices))
- [x] (not needed) States are translated in the frontend (text-based sensors only, [docs](internationalization_index.md))
- [ ] Tests for reading data from/controlling the integration ([docs](development_testing.md))
- [ ] Has a code owner

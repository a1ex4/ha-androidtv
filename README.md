# media_player-androidtv


## 0. Checklist for creating a platform

### 0.0 Common

 1. Follow our [Style guidelines](development_guidelines.md)
- [x] Use existing constants from [`const.py`](https://github.com/home-assistant/home-assistant/blob/dev/homeassistant/const.py)

### 0.1 Requirements

- [x] Requirement version should be pinned: `REQUIREMENTS = ['phue==0.8.1']`
- [x] We no longer want requirements hosted on GitHub. Please upload to PyPi.
- [x] Requirements should only be imported inside functions. This is necessary because requirements are installed on the fly.

### 0.2 Dependencies

- [x] If you depend on a component for the connection, add it to your dependencies: `DEPENDENCIES = ['nest']`

### 0.3 Configuration

- [x] Voluptuous schema present for [configuration validation](development_validation.md)
- [ ] Voluptuous schema extends schema from component<br>(e.g., `light.hue.PLATFORM_SCHEMA` extends `light.PLATFORM_SCHEMA`)
- [x] Default parameters specified in voluptuous schema, not in `setup_platform(...)`
- [x] Your `PLATFORM_SCHEMA` should use as many generic config keys as possible from `homeassistant.const`

- [x] Never depend on users adding things to `customize` to configure behavior inside your platform.

### 0.4 Setup Platform

- [ ] Test if passed in info (user/pass/host etc.) works.
- [ ] Group your calls to `add_devices` if possible.
- [ ] If platform adds extra services, format should be `<component>.<platform>_<service name>`.

### 0.5 Entity

- [x] Extend entity from component, e.g., `class HueLight(Light)`.
- [x] Avoid passing in `hass` as a parameter to the entity. When the entity has been added to Home Assistant, `hass` will be set on the entity by the helper in entity_platform.py. This means you can access `hass` as `self.hass` inside the entity.
- [x] Do not call `update()` in constructor, use `add_entities(devices, True)` instead.
- [x] Do not do any I/O inside properties. Cache values inside `update()` instead.
- [x] The state and/or attributes should not contain relative time since something happened. Instead it should store UTC timestamps.

### 0.6 Communication with devices/services

- [x] All API specific code has to be part of a third party library hosted on PyPi. Home Assistant should only interact with objects and not make direct calls to the API.

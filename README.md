
# **Important message**
> 
> This a fork of the existing archived project created by vlebourl. Please contribute here.

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub release](https://img.shields.io/github/v/release/vlebourl/custom_vesync.svg)](https://GitHub.com/vlebourl/custom_vesync/releases/)

# VeSync custom component for Home Assistant

Custom component for Home Assistant to interact with smart devices via the VeSync platform.
This integration is heavily based on [VeSync_bpo](https://github.com/borpin/vesync-bpo) and relies on [pyvesync](https://github.com/webdjoe/pyvesync) under the hood.

## Installation

This integration will override the core VeSync integration.

Easiest install is via [HACS](https://hacs.xyz/):

1. Click the button below to add this repository to HACS.

   [![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=micahqcade&repository=custom_vesync&category=integration)
3. Install this integration via HACS.
4. Restart Home Assistant.
5. Configure the 'VeSync' integration via the integrations page or press the blue button below.

<details>
  <summary>Alternative: Manual Install</summary>

1. Copy the `custom_components/vesync` to your `custom_components` folder. Reboot Home Assistant and configure the 'VeSync' integration via the integrations page or press the blue button below.
</details>

6. Click the button below to setup the integration.

   [![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=vesync)

You can make sure the custom integration is in use by looking for the following icon in the Settings > Devices & Services page:
![image](https://user-images.githubusercontent.com/5701372/234820776-11a80f79-5b4d-4dbe-8b63-42579e4a5631.png)

## Logging

### Enable debug logging

The [logger](https://www.home-assistant.io/integrations/logger/) integration lets you define the level of logging activities in Home Assistant. Turning on debug mode will show more information about unsupported devices in your logbook.

```yaml
logger:
  default: error
  logs:
    custom_components.vesync: debug
    pyvesync: debug
```

## TODO LIST
```
- [x] Air Fryer Properties (AirFryer158)
- [ ] Air Fryer Methods
- [ ] Create the Card
```

### Contributing

All contributions are very welcomed!
Please make sure to install `pre-commit` and run the pre-commit hook before submitting a PR.

```sh
pip install pre-commit
pre-commit install
pre-commit run --all-files
```


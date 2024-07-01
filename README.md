
# **Important message**
> 
> This a fork of the existing archived project created by vlebourl. Please contribute here.

<!---[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)-->
[![GitHub release](https://img.shields.io/github/v/release/micahqcade/custom_vesync.svg)](https://GitHub.com/micahqcade/custom_vesync/releases/)

# VeSync custom component for Home Assistant

Custom component for Home Assistant to interact with smart devices via the VeSync platform.
This integration is heavily based on [VeSync_bpo](https://github.com/borpin/vesync-bpo) and relies on [pyvesync](https://github.com/webdjoe/pyvesync) under the hood.

## Installation

You can install this integration via [HACS](#hacs) or [manually](#manual).
This integration will override the core VeSync integration.

### HACS

This integration can be installed by adding this repository to HACS __AS A CUSTOM REPOSITORY__, then searching for `Custom VeSync`, and choosing install. Reboot Home Assistant and configure the 'VeSync' integration via the integrations page or press the blue button below.

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=vesync)

### Manual

Copy the `custom_components/vesync` to your `custom_components` folder. Reboot Home Assistant and configure the 'VeSync' integration via the integrations page or press the blue button below.

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=vesync)

You can make sure the custom integration is in use by looking for the following icon in the Settings > Devices & Services page:
![image](https://user-images.githubusercontent.com/5701372/234820776-11a80f79-5b4d-4dbe-8b63-42579e4a5631.png)

## Logging

### Enable debug logging

#### Via Home Assistant UI

Navigate to the Vesync integration and click on `Enable debug logging`. Restart Home Assistant. Give it a few minutes and navigate back to the Vesync integration and disable debug logging. A local log file will get downloaded to your device.

![image](https://github.com/RobertD502/custom_vesync/assets/52541649/c556458c-a0a6-4432-acec-1200fc561d79)



#### YAML Method

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


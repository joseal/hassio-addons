![Logo][logo]

# Ecoforest Proxy
A proxy server Home Assistant addon for Ecoforest stoves.

![Supports aarch64 Architecture][aarch64-shield] ![Supports amd64 Architecture][amd64-shield] ![Supports armhf Architecture][armhf-shield] ![Supports armv7 Architecture][armv7-shield] ![Supports i386 Architecture][i386-shield]

## About
This addon is based on a Python script initially wrote by Nuno Lopes and it allows to control Ecoforest stoves from Home Assistant, by implementing a proxy service that parses the data provided by the stove firmware and produces a response in a JSON format.

[EcoForest][ecoforest] is a Spanish Company founded in 1959 (by Jose Carlos Alonso), that produces pellet stoves among other heater systems. Their focus is "develop innovative products that were both economic and environmentally-friendly, with the intention of making the world a better place".

This addon is not developed or supported by Ecoforest, so for support or in case you find any issues with the addon, please check the [issue tracker][issue] for similar issues and be free to create a new one if needed.

This is an open project, so please feel free to create a PR for fixes and enhancements.

## Installation
1. Add the repository URL via the Hassio Add-on Store Tab:

   https://github.com/joseal/hassio-addons

2. Install the Ecoforest Proxy addon

## Configuration

### Add-on configuration:

        debug: false
        domestic_hot_water: false
        proxy_port: '8998'
        ecoforest_host: 'http://192.168.1.70'
        ecoforest_user: '12345678901'
        ecoforest_pass: Password

#### Option: debug (required)

If set to false, additoinal logging information will be add to log 

#### Option: domestic_hot_water (required)

If set to false, meaning is used a domestic hot water accumulator connected to stove

#### Option: proxy_port (required)

TCP port where the proxy service will be listening 

#### Option: ecoforest_host (required)

Base URL of your stove

#### Option: ecoforest_user (required)

Username used to access the stove web interface

#### Option: ecoforest_pass (required)

Password used to access the stove web interface


### Home Assistant configuration:

```yaml
#### Option: domestic_hot_water (required)

If set to true, meaning is used a domestic hot water accumulator connected to stove

#### Option: proxy_port (required)

TCP port where the proxy service will be listening

#### Option: ecoforest_host (required)

Base URL of your stove

#### Option: ecoforest_user (required)

Username used to access the stove web interface

#### Option: ecoforest_pass (required)

Password used to access the stove web interface

### Home Assistant configuration:

```yaml
sensor:
  - platform: rest
    name: ecoforest
    resource: "http://192.168.0.254:8998/ecoforest/fullstats"
    method: "GET"
    scan_interval: 10
    force_update: true
    json_attributes:
      - temperatura
      - consigna_potencia
      - modo_func
      - modo_operacion
      - state
      - on_off
      - consigna_temperatura
      - estado
      - error_MODO_on_off
  - platform: template
    sensors:
      ecoforest_status:
        entity_id: sensor.ecoforest
        friendly_name: "Status"
        value_template: "{{ state_attr('sensor.ecoforest', 'state') }}"
      ecoforest_temp:
        entity_id: sensor.ecoforest
        friendly_name: "Temperature"
        unit_of_measurement: "°C"
        value_template: "{{ state_attr('sensor.ecoforest', 'consigna_temperatura') }}"
      ecoforest_potencia:
        entity_id: sensor.ecoforest
        friendly_name: "Power"
        value_template: "{{ state_attr('sensor.ecoforest', 'consigna_potencia') }}"
      ecoforest_room_temp:
        entity_id: sensor.ecoforest
        friendly_name: "Room Temperature"
        unit_of_measurement: "°C"
        value_template: "{{ state_attr('sensor.ecoforest', 'temperatura') }}"

  - platform: rest
    name: ecoforest_operation_temps
    resource: "http://192.168.0.254:8998/ecoforest/operationtemps"
    method: "GET"
    scan_interval: 10
    force_update: true
    json_attributes:
      - error_get_meas_agua
      - Aa
      - " Ab"
      - " Ac"
      - " Ad"
      - " Ae"
      - " Af"
      - " Ag"
      - " Ah"
      - " Ai"
  - platform: template
    sensors:
      ecoforest_aqs_temp:
        entity_id: sensor.ecoforest_operation_temps
        friendly_name: "DHW Temperature"
        unit_of_measurement: "°C"
        value_template: "{{ state_attr('sensor.ecoforest_operation_temps', ' Ac') }}"
      ecoforest_impulsao_temp:
        entity_id: sensor.ecoforest_operation_temps
        friendly_name: "Impulsao Temperature"
        unit_of_measurement: "°C"
        value_template: "{{ state_attr('sensor.ecoforest_operation_temps', 'Aa') }}"
      ecoforest_retorno_temp:
        entity_id: sensor.ecoforest_operation_temps
        friendly_name: "Return Temperature"
        unit_of_measurement: "°C"
        value_template: "{{ state_attr('sensor.ecoforest_operation_temps', ' Ab') }}"
      ecoforest_heating_temp:
        entity_id: sensor.ecoforest_operation_temps
        friendly_name: "Heating Temperature"
        unit_of_measurement: "°C"
        value_template: "{{ state_attr('sensor.ecoforest_operation_temps', ' Af') }}"

  - platform: rest
    name: ecoforest_configuration_temps
    resource: "http://192.168.0.254:8998/ecoforest/configtemps"
    method: "GET"
    scan_interval: 10
    force_update: true
    json_attributes:
      - error_get_set_meas_agua
      - Ba
      - " Bb"
      - " Bc"
      - " Bd"
      - " Be"
      - " Bf"
      - " Bg"
      - " Bh"
      - " Bi"
      - " Bj"
      - " Bk"
      - " Bl"
      - " Bm"
      - " Bn"
      - " AD"
  - platform: template
    sensors:
      ecoforest_aqs_requested_temp:
        entity_id: sensor.ecoforest_configuration_temps
        friendly_name: "DHW Requested Temperature"
        unit_of_measurement: "°C"
        value_template: "{{ state_attr('sensor.ecoforest_configuration_temps', 'Ba') }}"
      ecoforest_ambiente_requested_temp:
        entity_id: sensor.ecoforest_configuration_temps
        friendly_name: "Ambiente Requested Temperature"
        unit_of_measurement: "°C"
        value_template: "{{ state_attr('sensor.ecoforest_configuration_temps', ' Be') }}"
      ecoforest_delte_aqs_temp:
        entity_id: sensor.ecoforest_configuration_temps
        friendly_name: "Delta DHW Temperature"
        unit_of_measurement: "°C"
        value_template: "{{ state_attr('sensor.ecoforest_configuration_temps', ' Bc') }}"
      ecoforest_requested_aqs_pump_temp:
        entity_id: sensor.ecoforest_configuration_temps
        friendly_name: "Requested DHW Pump Temperature"
        unit_of_measurement: "°C"
        value_template: "{{ state_attr('sensor.ecoforest_configuration_temps', ' Bj') }}"
      ecoforest_heating_requested_pump_temp:
        entity_id: sensor.ecoforest_configuration_temps
        friendly_name: "Heating Requested Pump Temperature"
        unit_of_measurement: "°C"
        value_template: "{{ state_attr('sensor.ecoforest_configuration_temps', ' Bk') }}"

  - platform: rest
    name: ecoforest_operation
    resource: "http://192.168.0.254:8998/ecoforest/operationmode"
    method: "GET"
    scan_interval: 10
    force_update: true
    json_attributes:
      - error_get_CONTROL_CLIMA_INVIERNO
      - CONTROL_CLIMA_INVIERNO
      - state
  - platform: template
    sensors:
      ecoforest_operation_mode:
        entity_id: sensor.ecoforest_operation
        friendly_name: "Get Operation Mode"
        value_template: "{{ state_attr('sensor.ecoforest_operation', 'CONTROL_CLIMA_INVIERNO') }}"
      ecoforest_operation_mode_state:
        friendly_name: "Operation Mode State"
        value_template: "{{ state_attr('sensor.ecoforest_operation', 'state') }}"
```
## Credits:

- [NunoLopes][nuno]

[logo]: https://github.com/joseal/hassio-addons/raw/master/ecoforest-proxy/icon.png
[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
[armhf-shield]: https://img.shields.io/badge/armhf-yes-green.svg
[armv7-shield]: https://img.shields.io/badge/armv7-yes-green.svg
[i386-shield]: https://img.shields.io/badge/i386-yes-green.svg
[issue]: https://github.com/home-assistant/hassio-addons/issues
[ecoforest]: https://ecoforest.com/en
[nuno]: https://github.com/nunolopes/ecoforest-proxy

[i386-shield]: https://img.shields.io/badge/i386-yes-green.svg

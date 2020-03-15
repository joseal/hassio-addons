![Logo][logo]

# Ecoforest Proxy
A proxy server for Ecoforest stoves

![Supports aarch64 Architecture][aarch64-shield] ![Supports amd64 Architecture][amd64-shield] ![Supports armhf Architecture][armhf-shield] ![Supports armv7 Architecture][armv7-shield] ![Supports i386 Architecture][i386-shield]

## Home Assistant config

```yaml
sensor:
  - platform: rest
    name: ecoforest
    resource: 'http://192.168.0.254:8998/ecoforest/fullstats'
    method: 'GET'
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
```

[logo]: https://github.com/joseal/hassio-addons/raw/master/ecoforest-proxy/icon.png
[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
[armhf-shield]: https://img.shields.io/badge/armhf-yes-green.svg
[armv7-shield]: https://img.shields.io/badge/armv7-yes-green.svg
[i386-shield]: https://img.shields.io/badge/i386-yes-green.svg
# gwxhaus
## Greenhouse Controller

*It's just started, not finished.*

Open hardware and firmware to control a greenhouse heating and cooling. Depends on temperature, humidity, wind and time.

An ESP32 controls the motor-controller and reads sensor data.

### Sensors
- Temperature in/out
- Humidity in/out
- Wind
- Soil moisture

There can be a lot of settings depending on sensor values and time.

### Actors
- Motors to open/close the windows
- Valves to control water

The ESP32 is connected via another ESP32, ESP8266 or RaspberryPi to the WWW. Via mqtt the sensor data and actor positions are stored in a database and can be viewd in charts.

Optional, password protected, it's possible to change the settings and manually control the actors.

If any sensor values are out of range, or power fails, there can be messages sent via email, telegram, SMS, telephone (voip), or other channels.

Weather forecast data from Deutscher Wetterdienst https://dwd.api.bund.dev/ can be used to protect windows against storm or hail.

# Vocal Personal Assistant


Raspberry Pi OS
```shell
sudo apt update
sudo apt full-upgrade
```

Configuration tool

```shell
sudo raspi-config
```

Add a WiFi network
```shell
sudo nano /etc/wpa_supplicant/wpa_supplicant.conf
```
add network details
```
network={
        ssid="name"
        psk="password"
}
```
and run
```shell
wpa_cli -i wlan0 reconfigure
```
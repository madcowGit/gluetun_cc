# Custom component for Home Assistant: Gluetun status
Custom component for home assistant that reads information from [Gluetun VPN client](https://github.com/qdm12/gluetun)
Extracts data about the VPN connection from the JSON provided by the HTTP Control Server.

thanks to qdm12 for the excellent [Gluetun VPN client](https://github.com/qdm12/gluetun)

# sensors
| sensor | from link | 
|--------|--------|
| status | http://ipaddress:port/v1/openvpn/status |
| public ip | http://ipaddress:port/v1/publicip/ip | 
| country | http://ipaddress:port/v1/publicip/ip | 

# Installation 
## (simple)
* Copy to custom_component folder
* add through UI

## (symbolic link)
* clone git repository
* in custom_components create a symbolic link to the cloned folder

## Gluetun requirements
# HTTP Control Server
[HTTP Control Server](https://github.com/qdm12/gluetun-wiki/blob/main/setup/advanced/control-server.md) must be enabled

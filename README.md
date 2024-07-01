# QKD-App-VPN

## Post Quantum VPN and Videocall enhanced by QKD Application
<p float="left">
    <img src="upb.png" alt="University Politehnica of Bucharest" width="50"/>
    <img src="Logo.png" alt="Quantum Team @ UPB" width="100"/>
</p>

### Description

This application implements a configuration generator for an [open source post quantum VPN - Wireguard](https://www.wireguard.com/) and [open source VOIP software](https://www.linphone.org/).

This application has been developed by the Quantum Team @ UPB, and is provided to everyone for fair usage according to the License.

### Features

- Fast configuration generator for setting up a post quantum VPN.
  
### Requirements

- A point-to-point connection to a QKD device that can be used by the [QKDGKT](https://github.com/QuantumUPB/QKD-Infra-GetKey) module.
- A server with a known public IP on which to run the Wireguard server.
- `python3` installed.
- Wireguard installed, you can choose your installation method [here](https://www.wireguard.com/install/).
- Linphone installed, with desktop installation options [here](https://new.linphone.org/technical-corner/linphone?qt-technical_corner=2#qt-technical_corner).

### Configuring the clients

Download the `qkdgkt` module along the `main.py` script.

`git clone git@github.com:QuantumUPB/QKD-Infra-GetKey.git`

Start the application. 

`python3 main.py`

Select the `client` button, and follow the steps that are highlighted:

- Generate WireGuard key pair
- Acquire QKD Key - you will need this key when configuring the server
- Generate WireGuard Config

Afterwards, with the generated client configuration file, open Wireguard, and select `Import `Tunnel(s) from File`, choosing the generated configuration file. Before enabling the tunnel, the Wireguard server needs to be up.

### Configuring the server

Start the application. 

`python3 main.py`

Select the `server` button, and follow the steps that are highlighted:

- Generate WireGuard key pair
- Add allowed peers, with the peer IP, peer public key and peer QKD key ID, all copied from the client configurations
- Generate WireGuard Config

With the generated server configuration file, open Wireguard and import the generated config. Alternatively, if running the server on a different machine, you need to upload the config to the server and put it in the following location:

`sudo cp ./wg_server.conf /etc/wireguard/wg0.conf`

Now, start the Wireguard server

`sudo wg-quick up wg0`

Ensure that the server's firewall configuration will allow wireguard traffic, and will also allow ip4 and ipv6 forwarding.

### Start a videoconference over the Post-Quantum VPN enhanced by QKD

When the Wireguard server is up, the clients can start the tunnels, entering the VPN.

Afterwards, from the application, press the `Launch VideoCall` button, which will launch the Linphone application. There, you'll need to Settings->Preferences->Network and set your port to 5060 if it is configured differently. Ensure that your firewall allows traffic on this port. Afterwards, you'll need to exchange the SIP account with the other participants in the video call. Ensure that the SIP accounts include the IP configured in your Wireguard configuration. If these do not have the VPN IP's, restart the Linphone application. After adding the other participants to the known contacts, you can initiate the video-call over the post quantum VPN enhanced by QKD.

### Security considerations

- The machines which run this application should have a point to point connection to the QKD devices in order to maintain the unconditional security of this protocol.

### Copyright and license

This work has been implemented by Alin-Bogdan Popa and Bogdan-Calin Ciobanu, under the supervision of prof. Pantelimon George Popescu, within the Quantum Team in the Computer Science and Engineering department,Faculty of Automatic Control and Computers, National University of Science and Technology POLITEHNICA Bucharest (C) 2024. In any type of usage of this code or released software, this notice shall be preserved without any changes.

If you use this software for research purposes, please follow the instructions in the "Cite this repository" option from the side panel.

This work has been partly supported by RoNaQCI, part of EuroQCI, DIGITAL-2021-QCI-01-DEPLOY-NATIONAL, 101091562.

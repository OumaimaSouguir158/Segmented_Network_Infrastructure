# Securing a segmented network infrastructure

## Objective
To design a segmented network architecture with firewalls and a VPN to
isolate different trust zones (users, servers, DMZ).

## Contents
```
network_diagram.md               → architecture diagram (VLAN10/20/30 + VPN)
pfsense_config/firewall_rules.txt → commented pfSense rule set
openvpn/server.conf               → OpenVPN server configuration (hardened)
openvpn/client.conf.template      → standard client profile
segmentation_test.py             → rule engine + 10 automated segmentation tests
```

## Technical stack
pfSense · VLAN · OpenVPN (AES-256-GCM, tls-crypt) · virtualised
environment (VirtualBox/GNS3).

## Running the segmentation tests
```bash
python3 segmentation_test.py
```
The script translates the pfSense rules into a small sequential evaluation engine
(first match = decision, like a true stateful firewall) and
replays 10 real-world traffic scenarios between zones.

## Vulnerability detected by the tests (real-world feedback)
The first version of the rules mistakenly allowed the VPN
(`10.8.0.0/24`) to reach the public DMZ (`192.168.30.10:443`), as the
general rule `pass any -> DMZ` was evaluated before any restrictions
specific to the VPN. The automated test `VPN -> DMZ (outside authorised perimeter)`
failed (`❌ FAIL`), revealing the inconsistency. **Fix**: added an
explicit and more specific blocking rule
(`block VLAN20 from 10.8.0.0/24 to 192.168.30.0/24  


Prior to the general
rule — all 10 scenarios now pass. This episode provides a
concrete illustration of why the systematic verification of segmentation
(and not just its design) is an integral part of defence in
depth.

## Concepts demonstrated
Network segmentation, defence in depth, VPN, management of
firewall rules, non-regression testing of a security policy.

# Architecture réseau segmentée — Schéma

```
                              INTERNET
                                 │
                          ┌──────┴──────┐
                          │   pfSense   │  (pare-feu / routeur périmétrique)
                          │  WAN : em0  │
                          └──┬───┬───┬──┘
                 VLAN 10     │   │   │     VLAN 30
              (Utilisateurs) │   │   │      (DMZ)
                    ┌────────┘   │   └────────┐
                    │            │            │
            ┌───────┴──────┐ ┌──┴───────┐ ┌───┴──────────┐
            │  LAN Users   │ │ VLAN 20   │ │  DMZ         │
            │ 192.168.10.0 │ │ Serveurs  │ │ 192.168.30.0 │
            │     /24      │ │192.168.20 │ │     /24      │
            └──────────────┘ │   .0/24   │ │ (Web, Mail)  │
                              └───────────┘ └──────────────┘

  VPN distant (OpenVPN, 10.8.0.0/24) ──► accès limité à VLAN 20 uniquement
```

## Zones de confiance
| VLAN | Zone | Plage IP | Accès autorisé sortant | Accès autorisé entrant |
|---|---|---|---|---|
| 10 | Utilisateurs (LAN) | 192.168.10.0/24 | Internet, DMZ (HTTP/HTTPS) | — |
| 20 | Serveurs internes | 192.168.20.0/24 | DMZ (DB uniquement) | LAN Users (apps internes), VPN |
| 30 | DMZ (Web/Mail publics) | 192.168.30.0/24 | Internet | Internet (80/443), LAN Users |
| VPN | Télétravail | 10.8.0.0/24 | VLAN 20 (accès limité) | — |

**Principe appliqué : défense en profondeur** — aucune communication directe
Internet → VLAN 20 ; la DMZ agit comme zone tampon pour tout service exposé.

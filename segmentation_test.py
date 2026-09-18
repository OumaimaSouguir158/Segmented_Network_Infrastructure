#!/usr/bin/env python3
"""
segmentation_test.py — Moteur de règles de pare-feu simplifié + suite de tests
automatisés vérifiant que la segmentation réseau (VLAN10/20/30 + VPN) respecte
bien la politique de cloisonnement définie dans pfsense_config/firewall_rules.txt.

Ce script simule, en Python, l'évaluation séquentielle des règles pfSense
(première règle qui matche = décision), puis exécute des scénarios de test
représentant des flux réels (Users→DMZ, Users→Serveurs, DMZ→Serveurs, etc.)
afin de prouver que le cloisonnement inter-zones est effectif.

Auteure : Oumaima Souguir — Master CDSI (UPHF)
"""

import ipaddress
from dataclasses import dataclass


@dataclass
class Rule:
    action: str        # "pass" ou "block"
    src: str           # réseau CIDR ou "any"
    dst: str           # réseau CIDR, IP unique, ou "any"
    proto: str         # "tcp", "udp", "any"
    ports: set | None  # ports autorisés, None = tous


def in_network(ip: str, network: str) -> bool:
    if network == "any":
        return True
    if "/" in network:
        return ipaddress.ip_address(ip) in ipaddress.ip_network(network)
    return ip == network


# Politique traduite depuis pfsense_config/firewall_rules.txt
#
# ⚠️ CORRECTIF appliqué suite aux tests automatisés (voir README, section
# "Faille détectée par les tests") : les règles "pass any -> DMZ" étaient
# évaluées AVANT toute restriction du VPN, ce qui autorisait par erreur
# le VPN (10.8.0.0/24) à atteindre la DMZ. Ajout de règles de blocage
# explicites, plus spécifiques, avant les règles générales "any".
RULES = [
    Rule("pass", "192.168.10.0/24", "192.168.30.0/24", "tcp", {80, 443}),
    Rule("pass", "192.168.10.0/24", "any", "tcp", {80, 443}),
    Rule("pass", "192.168.10.0/24", "192.168.20.10", "tcp", {8443}),
    Rule("block", "192.168.10.0/24", "192.168.20.0/24", "any", None),

    Rule("pass", "192.168.20.0/24", "192.168.30.20", "tcp", {5432}),
    Rule("pass", "10.8.0.0/24", "192.168.20.0/24", "tcp", {22, 443}),
    Rule("block", "10.8.0.0/24", "192.168.30.0/24", "any", None),   # correctif : VPN -/-> DMZ
    Rule("block", "192.168.20.0/24", "any", "any", None),

    Rule("pass", "any", "192.168.30.10", "tcp", {80, 443}),
    Rule("pass", "any", "192.168.30.11", "tcp", {25}),
    Rule("block", "192.168.30.0/24", "192.168.20.0/24", "any", None),
    Rule("block", "192.168.30.0/24", "192.168.10.0/24", "any", None),

    Rule("block", "any", "any", "any", None),  # deny all final
]


def evaluate(src_ip, dst_ip, proto, port):
    """Évalue le flux contre les règles, dans l'ordre, jusqu'au premier match."""
    for rule in RULES:
        proto_ok = rule.proto == "any" or rule.proto == proto
        port_ok = rule.ports is None or port in rule.ports
        if in_network(src_ip, rule.src) and in_network(dst_ip, rule.dst) and proto_ok and port_ok:
            return rule.action
    return "block"


TEST_SCENARIOS = [
    # (description, src, dst, proto, port, résultat attendu)
    ("Users -> Web DMZ (HTTPS)",            "192.168.10.50", "192.168.30.10", "tcp", 443, "pass"),
    ("Users -> Serveur interne non déclaré", "192.168.10.50", "192.168.20.15", "tcp", 3306, "block"),
    ("Users -> App RH déclarée",            "192.168.10.50", "192.168.20.10", "tcp", 8443, "pass"),
    ("DMZ compromise -> Serveurs internes",  "192.168.30.10", "192.168.20.15", "tcp", 22, "block"),
    ("DMZ compromise -> LAN Users",          "192.168.30.10", "192.168.10.50", "tcp", 445, "block"),
    ("VPN admin -> Serveurs (SSH)",          "10.8.0.5",      "192.168.20.15", "tcp", 22, "pass"),
    ("VPN -> DMZ (hors périmètre autorisé)", "10.8.0.5",      "192.168.30.10", "tcp", 443, "block"),
    ("Serveur interne -> Internet direct",   "192.168.20.15", "8.8.8.8",       "tcp", 443, "block"),
    ("Internet -> Mail DMZ (SMTP)",          "203.0.113.9",   "192.168.30.11", "tcp", 25, "pass"),
    ("Internet -> Serveur interne (direct)", "203.0.113.9",   "192.168.20.15", "tcp", 22, "block"),
]


def run_tests():
    print(f"{'Scénario':45} {'Attendu':8} {'Obtenu':8} {'Résultat'}")
    print("-" * 80)
    passed = 0
    for desc, src, dst, proto, port, expected in TEST_SCENARIOS:
        result = evaluate(src, dst, proto, port)
        ok = result == expected
        passed += ok
        status = "✅ OK" if ok else "❌ ÉCHEC"
        print(f"{desc:45} {expected:8} {result:8} {status}")
    print("-" * 80)
    print(f"{passed}/{len(TEST_SCENARIOS)} scénarios de cloisonnement conformes à la politique.")
    return passed == len(TEST_SCENARIOS)


if __name__ == "__main__":
    all_ok = run_tests()
    exit(0 if all_ok else 1)

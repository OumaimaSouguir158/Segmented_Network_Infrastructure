# Projet 3 — Sécurisation d'une infrastructure réseau segmentée

Niveau avancé 🔴 · ~5-6 semaines
**Master visé :** Cyberdéfense et Sécurité de l'Information (CDSI) — UPHF

## Objectif
Concevoir une architecture réseau segmentée avec pare-feu et VPN pour
cloisonner différentes zones de confiance (utilisateurs, serveurs, DMZ).

## Contenu
```
network_diagram.md               → schéma de l'architecture (VLAN10/20/30 + VPN)
pfsense_config/firewall_rules.txt → jeu de règles pfSense commenté
openvpn/server.conf               → configuration serveur OpenVPN (durcie)
openvpn/client.conf.template      → profil client type
segmentation_test.py             → moteur de règles + 10 tests automatisés de cloisonnement
```

## Stack technique
pfSense · VLAN · OpenVPN (AES-256-GCM, tls-crypt) · environnement
virtualisé (VirtualBox/GNS3).

## Exécuter les tests de cloisonnement
```bash
python3 segmentation_test.py
```
Le script traduit les règles pfSense en un petit moteur d'évaluation
séquentiel (premier match = décision, comme un vrai pare-feu à états) et
rejoue 10 scénarios de flux réels entre zones.

## Faille détectée par les tests (retour d'expérience réel)
La première version des règles autorisait, par erreur, le VPN
(`10.8.0.0/24`) à atteindre la DMZ publique (`192.168.30.10:443`), car la
règle générale `pass any -> DMZ` était évaluée avant toute restriction
spécifique au VPN. Le test automatisé `VPN -> DMZ (hors périmètre autorisé)`
a échoué (`❌ ÉCHEC`), révélant l'incohérence. **Correctif** : ajout d'une
règle de blocage explicite et plus spécifique
(`block VLAN20 from 10.8.0.0/24 to 192.168.30.0/24`) avant la règle
générale — les 10 scénarios passent désormais. Cet épisode illustre
concrètement pourquoi la vérification systématique de la segmentation
(et pas seulement sa conception) fait partie intégrante de la défense en
profondeur.

## Concepts démontrés
Segmentation réseau, défense en profondeur, VPN, gestion des règles de
pare-feu, tests de non-régression sur une politique de sécurité.

## Ce que ça démontre au jury
Élargissement de la sécurité applicative vers la sécurité réseau,
complémentarité directement recherchée par le CDSI — et une rigueur de
vérification (tests automatisés) plutôt qu'une simple configuration
statique.

## Ligne CV
« Infrastructure réseau segmentée — VLAN, pfSense, VPN, défense en
profondeur, tests de cloisonnement automatisés. »

## Question d'entretien possible
Comment avez-vous vérifié que la segmentation empêchait bien la
communication entre zones non autorisées ?
→ Réponse type : en traduisant le jeu de règles pfSense en un petit moteur
de test Python rejouant des scénarios de flux représentatifs de chaque
paire de zones, ce qui a d'ailleurs permis de détecter une règle trop
permissive (VPN → DMZ) avant mise en production.

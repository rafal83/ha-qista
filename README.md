<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="custom_components/qista/brand/dark_logo.png">
    <img alt="Qista" src="custom_components/qista/brand/logo.png" width="280">
  </picture>
</p>

# 🦟 Qista Mosquito Trap - Home Assistant Custom Component (HACS)

[![HACS Custom Component](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz/)
[![Home Assistant](https://img.shields.io/badge/Home--Assistant-Supported-blue.svg)](https://www.home-assistant.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Intégration personnalisée **Home Assistant** compatible **HACS** permettant de connecter, surveiller et gérer vos bornes anti-moustiques connectées **QISTA**.

Cette intégration s'interface directement avec l'API Cloud GraphQL moderne de Qista (`https://core-2pqjioauna-ew.a.run.app/graphql`).

---

## 📋 Table des matières

- [Fonctionnalités](#-fonctionnalités)
- [Entités créées](#-entités-créées)
  - [Capteurs (Sensors)](#capteurs-sensors)
  - [Capteurs binaires (Binary Sensors)](#capteurs-binaires-binary-sensors)
  - [Boutons (Buttons)](#boutons-buttons)
- [Architecture & API](#-architecture--api)
- [Installation](#-installation)
  - [Méthode 1 : Via HACS (Recommandée)](#méthode-1--via-hacs-recommandée)
  - [Méthode 2 : Installation manuelle](#méthode-2--installation-manuelle)
- [Configuration](#-configuration)
- [Arborescence du projet](#-arborescence-du-projet)
- [Dépannage & Erreurs fréquentes](#-dépannage--erreurs-fréquentes)

---

## ✨ Fonctionnalités

- 🔐 **Configuration via l'interface graphique (Config Flow)** : aucun fichier YAML requis.
- 📡 **Découverte automatique des équipements** : synchronisation directe des bornes déclarées sur votre compte Qista.
- 📊 **Télémétrie des captures** : suivi des captures quotidiennes, hebdomadaires et totales.
- 🧪 **Surveillance des consommables** : estimation en jours restants du leurre olfactif et de la bouteille de CO2.
- ⚠️ **Alertes automatiques** : capteurs binaires dédiés signalant un niveau critique de CO2 ou de leurre.
- 🔄 **Réinitialisation des consommables** : boutons pour réinitialiser les compteurs de consommables après remplacement.

---

## 🎛️ Entités créées

Pour chaque borne Qista associée à votre compte, les entités suivantes sont créées :

### Capteurs (Sensors)
| Entité | Nom | Unité | Description |
|---|---|---|---|
| `sensor.<borne>_mosquitoe_catch_day` | Moustiques capturés aujourd'hui | moustiques | Nombre de captures enregistrées sur la journée en cours |
| `sensor.<borne>_mosquitoe_catch_week` | Moustiques capturés (7 jours) | moustiques | Cumul des captures sur les 7 derniers jours glissants |
| `sensor.<borne>_mosquitoe_catch_total` | Total des captures | moustiques | Total historique des captures de la borne |
| `sensor.<borne>_working_status` | Statut de marche | — | État opérationnel de la borne |
| `sensor.<borne>_operating_status` | Statut de fonctionnement | — | Mode de fonctionnement actif |
| `sensor.<borne>_sim_status` | Statut SIM | — | État de la carte SIM intégrée |
| `sensor.<borne>_bait_remaining_days` | Leurre restant | `j` | Estimation du nombre de jours restants pour le leurre |
| `sensor.<borne>_co2_remaining_days` | CO2 restant | `j` | Estimation du nombre de jours restants de CO2 |
| `sensor.<borne>_loaded_co2_bottle_label` | Bouteille CO2 | — | Type de bouteille de CO2 configurée |

### Capteurs binaires (Binary Sensors)
| Entité | Nom | Classe | Description |
|---|---|---|---|
| `binary_sensor.<borne>_is_connected` | Connecté au Cloud | `connectivity` | Indique si la borne est joignable par les serveurs |
| `binary_sensor.<borne>_is_low_bait` | Alerte niveau leurre | `problem` | Activé lorsqu'il reste 3 jours ou moins de leurre |
| `binary_sensor.<borne>_is_low_co2` | Alerte niveau CO2 | `problem` | Activé lorsqu'il reste 3 jours ou moins de CO2 |

### Boutons (Buttons)
| Entité | Nom | Description |
|---|---|---|
| `button.<borne>_reset_co2` | Réinitialiser compteur CO2 | Réinitialise la date de mise en place de la bouteille de CO2 |
| `button.<borne>_reset_bait` | Réinitialiser compteur Leurre | Réinitialise la date de mise en place du leurre |

---

## 🛠️ Architecture & API

L'intégration utilise l'API Cloud GraphQL officielle :

```text
[Home Assistant]
       │
       └── (HTTPS / Bearer JWT) ──> https://core-2pqjioauna-ew.a.run.app/graphql
                                     ├── mutation signIn (Authentification)
                                     ├── query bams      (Liste & télémétrie des bornes)
                                     └── mutation resetBamConsumables (Gestion consommables)
```

---

## 🚀 Installation

### Méthode 1 : Via HACS (Recommandée)

1. Dans Home Assistant, ouvrez **HACS**.
2. Cliquez sur les **trois points verticaux** (en haut à droite) > **Dépôts personnalisés** (*Custom repositories*).
3. Ajoutez l'URL de votre dépôt Git (`https://github.com/rafal83/ha-qista`).
4. Dans le champ **Type / Catégorie**, sélectionnez **Intégration** (*Integration*).
5. Cliquez sur **Ajouter**, puis sur **Télécharger**.
6. **Redémarrez Home Assistant**.

### Méthode 2 : Installation manuelle

1. Téléchargez ou clonez ce dépôt.
2. Copiez l'intégralité du répertoire `custom_components/qista` dans votre dossier Home Assistant :
   ```text
   <config_homeassistant>/custom_components/qista/
   ```
3. **Redémarrez Home Assistant**.

---

## ⚙️ Configuration

1. Rendez-vous dans : **Paramètres** > **Appareils et services**.
2. Cliquez sur le bouton **Ajouter une intégration** (en bas à droite).
3. Recherchez **Qista Mosquito Trap**.
4. Renseignez :
   - **Email** : l'adresse email de votre compte Qista.
   - **Mot de passe** : votre mot de passe Qista.
   - *(Optionnel)* URL GraphQL (pré-remplie avec l'endpoint officiel).
5. Cliquez sur **Valider**. Vos bornes et capteurs apparaîtront instantanément !

---

## 📁 Arborescence du projet

```text
ha-qista/
├── custom_components/
│   └── qista/
│       ├── brand/                # Images de marque officielles (Home Assistant)
│       │   ├── icon.png
│       │   ├── icon@2x.png
│       │   ├── logo.png
│       │   ├── logo@2x.png
│       │   ├── dark_logo.png
│       │   └── dark_logo@2x.png
│       ├── __init__.py           # Initialisation & cycle de vie du composant
│       ├── manifest.json         # Déclaration officielle Home Assistant
│       ├── const.py              # Constantes et endpoint GraphQL
│       ├── api.py                # Client GraphQL asynchrone (aiohttp)
│       ├── coordinator.py        # DataUpdateCoordinator (polling périodique)
│       ├── config_flow.py        # Interface utilisateur d'installation
│       ├── sensor.py             # Capteurs de captures et consommables
│       ├── binary_sensor.py      # Capteurs d'alerte et connectivité
│       ├── button.py             # Boutons de remise à zéro des consommables
│       └── translations/         # Fichiers de localisation (FR / EN)
│           ├── fr.json
│           └── en.json
├── icon.png                      # Icône du dépôt (HACS)
├── logo.png                      # Logo du dépôt (HACS)
├── hacs.json                     # Configuration HACS
├── LICENSE                       # Licence MIT
└── README.md                     # Documentation
```

---

## ❓ Dépannage & Erreurs fréquentes

### Erreur d'authentification (`invalid_auth`)
Vérifiez que vos identifiants correspondent exactement à ceux utilisés sur l'application mobile Qista.

### Aucune borne trouvée
Vérifiez que vos bornes sont bien enregistrées et actives dans votre compte sur l'application officielle Qista. L'intégration synchronise automatiquement les appareils rattachés à votre profil.

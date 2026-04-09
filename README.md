# 📊 Human Risk Analytics

### Modélisation quantitative d'un profil atypique

[![Streamlit](https://img.shields.io/badge/Made%20with-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://python.org)

---

**Et si on appliquait les outils du Market Risk à un profil humain ?**

Ce projet modélise 4 probabilités de succès personnelles comme des actifs financiers, puis leur applique les concepts quantitatifs du risk management : VaR, Stress Tests, Greeks, Capture Ratios. L'objectif : démontrer qu'un profil atypique est un **actif à haute convexité** — les pertes sont bornées, mais le potentiel de hausse est asymétrique.

---

## 🎯 Concepts quantitatifs couverts

| Concept | Application personnelle |
|---|---|
| **Value at Risk (VaR)** | "Risk of Giving Up" — VaR historique, paramétrique et Monte Carlo sur chaque probabilité |
| **Stress Tests** | Fermeture des programmes de stage, 10 refus consécutifs, crise de confiance à -40% |
| **Greeks (Δ Γ ν Θ)** | Delta (effort), Gamma (accélération HPI), Vega (antifragilité), Theta (coût de l'inaction) |
| **UpMarket / DownMarket** | Capture Ratios démontrant l'avantage asymétrique de la résilience |
| **Risk Dashboard** | Seuils, exceedances, alertes et historique des breaches |

---

## 🚀 Installation & Lancement

```bash
# Cloner le repo
git clone https://github.com/gaspardmeray-jpg/human-risk-analytics.git
cd human-risk-analytics

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# Installer les dépendances
pip install -r requirements.txt

# Lancer le dashboard
streamlit run app.py
```

Le dashboard s'ouvre automatiquement dans votre navigateur à `http://localhost:8501`.

---

## 📁 Structure du projet

```
human-risk-analytics/
│
├── app.py                    # Point d'entrée Streamlit
├── requirements.txt          # Dépendances Python
├── README.md                 # Ce fichier
│
├── data/
│   └── generate_data.py      # Génération des 4 séries temporelles synthétiques
│
├── models/
│   ├── var.py                # VaR historique, paramétrique, Monte Carlo
│   ├── stress_tests.py       # 3 scénarios de stress avec recovery
│   ├── greeks.py             # Delta, Gamma, Vega, Theta
│   └── updown_market.py      # Analyse UpMarket/DownMarket & Capture Ratios
│
├── components/
│   ├── overview.py           # Onglet Vue d'ensemble
│   ├── var_tab.py            # Onglet VaR & Monte Carlo
│   ├── stress_tab.py         # Onglet Stress Tests
│   ├── greeks_tab.py         # Onglet Greeks
│   ├── market_tab.py         # Onglet UpMarket/DownMarket
│   └── risk_dashboard.py     # Onglet Risk Dashboard
│
└── utils/
    └── styling.py            # Thème visuel et styles Plotly/Streamlit
```

---

## 📸 Aperçu

| Vue d'ensemble | VaR & Monte Carlo |
|:-:|:-:|
| *4 trajectoires de probabilité sur 24 mois* | *Distributions, cônes de confiance, 1000 simulations* |

| Stress Tests | Greeks |
|:-:|:-:|
| *Impact des chocs extrêmes et trajectoires de recovery* | *Sensibilités Delta, Gamma, Vega, Theta* |

| Up/Down Market | Risk Dashboard |
|:-:|:-:|
| *Capture Ratios et avantage asymétrique* | *Alertes, exceedances et registre des breaches* |

---

## 🧬 Les 4 métriques personnelles

- **Probabilité_Village** — Probabilité qu'un enfant de Lasson (village normand, 0 réseau finance) devienne Risk Analyst
- **Probabilité_BAC_1025** — Probabilité qu'un étudiant ayant eu 10.25/20 au BAC intègre la finance de marché
- **Probabilité_TDAH_TSA_HPI** — Probabilité qu'un profil neurodivergent (TDAH + TSA + HPI) performe en Risk Management
- **Probabilité_Ecole_NonTarget** — Probabilité qu'un étudiant d'école non-target décroche un stage en Market Risk

---

## 👤 À propos

Je m'appelle Gaspard. Je viens de Lasson, un village en Normandie où personne ne travaille en finance. J'ai eu 10.25 au BAC. Je suis diagnostiqué TDAH, TSA et HPI.

Sur le papier, je ne devrais pas postuler en Market Risk. Dans les faits, j'ai construit ce dashboard pour prouver que les outils quantitatifs du risk management — VaR, stress tests, greeks — s'appliquent aussi à un parcours humain. Et que les mêmes mécanismes qui font qu'un actif atypique est sous-évalué par le marché font aussi qu'un profil atypique est sous-évalué par les recruteurs.

**La résilience n'est pas un soft skill. C'est un avantage asymétrique quantifiable.**

---

## 📄 Licence

Ce projet est distribué sous licence MIT — voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

## 📬 Contact

Si vous êtes recruteur et que ce dashboard vous a intrigué, contactez-moi sur [LinkedIn](https://linkedin.com/in/gaspardmeray) ou par email à gaspard.meray@gmail.com.

# 🎭 COLPRAD 2025 - Plateforme de Billetterie Professionnelle

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1-green.svg)](https://flask.palletsprojects.com/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg)](https://getbootstrap.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Système de billetterie en ligne professionnel pour le **Colloque des Professionnels de l'Art pour le Développement (COLPRAD) 2025** - 13 Décembre 2025 à Lomé, Togo.

![COLPRAD 2025](https://img.shields.io/badge/Event-13%20D%C3%A9cembre%202025-orange)
![Location](https://img.shields.io/badge/Location-Lom%C3%A9%2C%20Togo-green)

---

## ✨ Caractéristiques

### 🎨 Design Professionnel
- ✅ Interface élégante et moderne
- ✅ Typographie professionnelle (Playfair Display + Inter)
- ✅ Palette de couleurs cohérente (Charte COLPRAD)
- ✅ Responsive parfait (mobile, tablet, desktop)
- ✅ Pas d'icônes superflues, focus sur le contenu
- ✅ Effets visuels sophistiqués (gradients, glassmorphism)

### 🎫 Système de Billetterie
- ✅ 3 types de billets (Standard 5K, Premium 15K, VIP 50K FCFA)
- ✅ Gestion des quotas en temps réel
- ✅ Codes promo avec réductions (pourcentage ou montant fixe)
- ✅ Génération automatique de QR codes uniques
- ✅ Badges PDF personnalisés (90×135mm)
- ✅ Numéros de commande uniques

### 💳 Paiement Sécurisé
- ✅ Intégration PayGate complète
- ✅ MoovMoney, Mixx By Yas, Carte bancaire
- ✅ Webhooks pour confirmation automatique
- ✅ Emails de confirmation instantanés (< 60 secondes)
- ✅ Gestion des statuts (pending, completed, failed, cancelled)

### 🌐 Multilingue
- ✅ Français / Anglais
- ✅ Changement de langue dynamique
- ✅ Contenu traduit sur toutes les pages

### 📊 Administration
- ✅ Tableau de bord complet avec statistiques
- ✅ Gestion des participants
- ✅ Export CSV des commandes
- ✅ Système d'alertes en temps réel
- ✅ Gestion des incidents
- ✅ Check-in via QR code
- ✅ Génération de badges en masse

### 📧 Communication
- ✅ Formulaire de contact
- ✅ Newsletter
- ✅ Espace presse
- ✅ Emails automatiques avec QR code

---

## 📅 Informations de l'Événement

| Information | Détail |
|-------------|--------|
| **Date** | 13 Décembre 2025 |
| **Horaires** | 14H00 - 17H00 |
| **Lieu** | Hôtel Elie Palace, Adidogomé |
| **Ville** | Lomé, Togo |
| **Participants** | 300+ attendus |
| **Intervenants** | 50+ experts |
| **Pays** | 15+ représentés |

---

## 🚀 Installation

### Prérequis
- Python 3.8+
- pip
- Git

### Étapes d'Installation

#### 1. Cloner le Projet
```bash
git clone https://github.com/DavenBANKA/Colprad.git
cd Colprad
```

#### 2. Créer un Environnement Virtuel
```bash
python -m venv .venv
```

#### 3. Activer l'Environnement
```bash
# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

#### 4. Installer les Dépendances
```bash
pip install -r requirements.txt
```

#### 5. Configurer les Variables d'Environnement
```bash
# Copier le fichier exemple
cp .env.example .env

# Éditer .env avec vos configurations
```

Variables importantes :
```env
SECRET_KEY=votre-cle-secrete
DATABASE_URL=sqlite:///colprad.db

# Email
MAIL_SERVER=smtp.gmail.com
MAIL_USERNAME=votre-email@gmail.com
MAIL_PASSWORD=votre-mot-de-passe

# PayGate
PAYGATE_API_KEY=votre-cle-api
PAYGATE_MERCHANT_ID=votre-merchant-id
PAYGATE_WEBHOOK_SECRET=votre-webhook-secret
```

#### 6. Initialiser la Base de Données
```bash
python
>>> from app import app, db
>>> with app.app_context():
...     db.create_all()
>>> exit()
```

#### 7. Lancer l'Application
```bash
python app.py
```

Le site sera accessible sur : **http://localhost:5000**

---

## 📁 Structure du Projet

```
Colprad/
├── app.py                      # Application Flask principale
├── models.py                   # Modèles de base de données
├── config.py                   # Configuration
├── badge_generator.py          # Génération de badges PDF
├── requirements.txt            # Dépendances Python
├── .env.example               # Exemple de configuration
├── .gitignore                 # Fichiers à ignorer
│
├── templates/                 # Templates HTML
│   ├── base.html             # Template de base
│   ├── index.html            # Page d'accueil
│   ├── tickets.html          # Billetterie
│   ├── checkout.html         # Paiement
│   ├── confirmation.html     # Confirmation
│   ├── payment_redirect.html # Redirection PayGate
│   ├── about.html            # À propos
│   ├── program.html          # Programme
│   ├── speakers.html         # Intervenants
│   ├── contact.html          # Contact
│   ├── press.html            # Presse
│   └── admin/                # Administration
│       ├── dashboard.html
│       ├── participants.html
│       ├── alerts.html
│       └── incidents.html
│
├── static/                    # Fichiers statiques
│   ├── css/
│   │   ├── style.css         # Styles principaux
│   │   └── responsive.css    # Styles responsive
│   └── js/
│       ├── main.js           # JavaScript principal
│       └── admin.js          # JavaScript admin
│
└── Documentation/             # Documentation complète
    ├── README_DESIGN.md
    ├── INTEGRATION_PAYGATE.md
    ├── DEPLOYMENT_GUIDE.md
    └── ...
```

---

## 💳 Configuration PayGate

### 1. Créer un Compte PayGate
Visitez https://www.paygate.tg et créez un compte marchand

### 2. Obtenir les Clés API
Dans le tableau de bord PayGate :
- API Key (auth_token)
- Merchant ID (shop_id)
- Webhook Secret

### 3. Configurer les URLs de Callback
- **Success URL** : `https://votre-domaine.com/payment/success/{order_number}`
- **Cancel URL** : `https://votre-domaine.com/payment/cancel/{order_number}`
- **Callback URL** : `https://votre-domaine.com/payment/callback`

### 4. Tester
Utilisez les cartes de test PayGate pour vérifier l'intégration

---

## 📊 Utilisation

### Pour les Visiteurs

1. **Consulter le Programme**
   - Accéder à `/program`
   - Voir les sessions et horaires

2. **Réserver un Billet**
   - Accéder à `/tickets`
   - Choisir le type de billet
   - Remplir le formulaire
   - Payer via PayGate
   - Recevoir l'email avec QR code

3. **Contacter l'Organisation**
   - Accéder à `/contact`
   - Remplir le formulaire
   - Recevoir une réponse sous 24h

### Pour les Administrateurs

1. **Accéder au Dashboard**
   - URL : `/admin/dashboard`
   - Voir les statistiques en temps réel

2. **Gérer les Participants**
   - URL : `/admin/participants`
   - Rechercher, filtrer, exporter

3. **Check-in**
   - Scanner le QR code
   - Valider l'entrée

4. **Générer des Badges**
   - Sélectionner les participants
   - Télécharger le PDF

---

## 🎨 Charte Graphique

### Couleurs Principales
- **Ivoire** : `#F9F6EF` - Fond principal
- **Bleu Nuit** : `#052B47` - Accent, en-têtes
- **Turquoise** : `#0E5E96` - Primaire, liens
- **Orange** : `#D8431A` - CTA, accents
- **Vert** : `#4E923D` - Success, validation

### Typographie
- **Titres** : Playfair Display (serif élégant)
- **Corps** : Inter (sans-serif moderne)

---

## 📧 Contact

### Événement
- **Email** : colpradofficiel@gmail.com
- **Téléphone** : +228 92 38 40 92

### Développeur
- **Email** : blaisederge@outlook.com
- **Téléphone** : +228 92 53 05 12
- **GitHub** : [@DavenBANKA](https://github.com/DavenBANKA)

---

## 📝 Documentation

Documentation complète disponible dans le projet :

- **README_DESIGN.md** - Vue d'ensemble du design
- **INTEGRATION_PAYGATE.md** - Guide d'intégration PayGate
- **DEPLOYMENT_GUIDE.md** - Guide de déploiement
- **LANCEMENT_RAPIDE.md** - Guide de démarrage rapide
- **VERIFICATION_FINALE.md** - Checklist complète

---

## 🤝 Contribution

Les contributions sont les bienvenues ! Pour contribuer :

1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

---

## 📜 License

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

---

## 🙏 Remerciements

- **Life Field Inc.** - Organisation
- **PayGate** - Solution de paiement
- **Bootstrap** - Framework CSS
- **Flask** - Framework Python
- **Google Fonts** - Typographie

---

## 📊 Statistiques du Projet

- **Lignes de code** : 14,000+
- **Fichiers** : 60+
- **Templates** : 20+
- **Documentation** : 15+ fichiers
- **Langues** : 2 (FR/EN)

---

## 🎯 Roadmap

### Version 1.0 (Actuelle) ✅
- [x] Site vitrine complet
- [x] Système de billetterie
- [x] Intégration PayGate
- [x] Administration complète
- [x] Design professionnel

### Version 1.1 (À venir)
- [ ] Application mobile
- [ ] Streaming en direct
- [ ] Chat en temps réel
- [ ] Système de notation
- [ ] Recommandations personnalisées

---

## 🌟 Fonctionnalités Avancées

### Sécurité
- ✅ Protection CSRF
- ✅ Validation des données
- ✅ Hachage des mots de passe
- ✅ HTTPS en production
- ✅ Webhooks sécurisés

### Performance
- ✅ Optimisation des requêtes
- ✅ Cache des ressources statiques
- ✅ Compression gzip
- ✅ Lazy loading des images

### SEO
- ✅ Meta tags optimisés
- ✅ URLs propres
- ✅ Sitemap.xml
- ✅ Robots.txt
- ✅ Schema.org markup

---

## 📱 Responsive Design

Le site est parfaitement responsive :

- **Mobile** (< 768px) : Navigation hamburger, boutons full-width
- **Tablet** (768-991px) : Layout adapté, 2 colonnes
- **Desktop** (≥ 992px) : Expérience complète, 3-4 colonnes

---

## 🎉 Événement COLPRAD 2025

Le COLPRAD est le rendez-vous incontournable des professionnels de la culture en Afrique de l'Ouest. Cette 3ème édition réunira plus de 300 participants pour échanger sur :

- Politiques culturelles et gouvernance
- Financement et mécénat culturel
- Networking et partenariats stratégiques
- Développement du secteur créatif

**Rejoignez-nous le 13 Décembre 2025 ! 🎭**

---

**Développé avec ❤️ par Daven BANKA pour Life Field Inc.**

**© 2025 COLPRAD - Tous droits réservés**

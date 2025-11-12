# COLPRAD 2025 - Site de Billetterie

Site de billetterie en ligne pour le Colloque des Professionnels de l'Art pour le Développement (COLPRAD).

## Fonctionnalités

- ✅ Site vitrine bilingue (FR/EN)
- ✅ Système de billetterie (Standard, Premium, VIP, Gratuit)
- ✅ Paiement en ligne (MoovMoney, Mixx By Yas, CB)
- ✅ Génération automatique de QR codes
- ✅ Génération de badges PDF professionnels (90×135mm)
- ✅ Envoi d'emails de confirmation
- ✅ Dashboard administrateur
- ✅ Export CSV des commandes et participants
- ✅ Système de codes promo
- ✅ Check-in via QR code
- ✅ Design responsive mobile-first
- ✅ Charte graphique COLPRAD respectée
- ✅ Liste complète des participants avec recherche

## Installation

### Prérequis
- Python 3.8+
- pip

### Étapes

1. Cloner le projet
```bash
git clone <repository-url>
cd colprad
```

2. Créer un environnement virtuel
```bash
python -m venv venv
```

3. Activer l'environnement virtuel
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

4. Installer les dépendances
```bash
pip install -r requirements.txt
```

5. Configurer les variables d'environnement
```bash
copy .env.example .env
```
Puis éditer `.env` avec vos configurations.

6. Initialiser la base de données
```bash
python
>>> from app import app, db
>>> with app.app_context():
...     db.create_all()
>>> exit()
```

7. Lancer l'application
```bash
python app.py
```

Le site sera accessible sur `http://localhost:5000`

## Structure du Projet

```
colprad/
├── app.py                 # Application Flask principale
├── config.py              # Configuration
├── models.py              # Modèles de base de données
├── requirements.txt       # Dépendances Python
├── .env.example          # Exemple de configuration
├── templates/            # Templates HTML
│   ├── base.html
│   ├── index.html
│   ├── tickets.html
│   ├── checkout.html
│   ├── confirmation.html
│   ├── about.html
│   ├── program.html
│   ├── speakers.html
│   ├── practical_info.html
│   ├── contact.html
│   ├── press.html
│   └── admin/
│       └── dashboard.html
└── static/               # Fichiers statiques
    ├── css/
    │   └── style.css
    └── js/
        └── main.js
```

## Configuration des Paiements

### PayGate
1. Créer un compte sur PayGate
2. Obtenir vos clés API
3. Configurer dans `.env`:
```
PAYGATE_API_KEY=votre-cle-api
PAYGATE_MERCHANT_ID=votre-merchant-id
PAYGATE_WEBHOOK_SECRET=votre-webhook-secret
```

## Configuration Email

Pour l'envoi des emails de confirmation:

```
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=votre-email@example.com
MAIL_PASSWORD=votre-mot-de-passe
```

## Types de Billets

| Type | Prix | Quota | Avantages |
|------|------|-------|-----------|
| Standard | 5,000 FCFA | 200 | Accès sessions, documentation |
| Premium | 15,000 FCFA | 100 | Standard + places réservées + pause café |
| VIP | 30,000 FCFA | 50 | Premium + VIP lounge + déjeuner + networking privé |
| Gratuit | 0 FCFA | 50 | Sur invitation uniquement |

## Routes Principales

### Public
- `/` - Page d'accueil
- `/tickets` - Billetterie
- `/order` - Commander un billet
- `/checkout` - Finaliser la commande
- `/confirmation/<order_number>` - Confirmation de commande
- `/badge/<order_number>` - Télécharger badge PDF
- `/about` - À propos
- `/program` - Programme
- `/speakers` - Intervenants
- `/practical-info` - Infos pratiques
- `/contact` - Contact
- `/press` - Espace presse

### Administration
- `/admin/dashboard` - Dashboard admin
- `/admin/participants` - Liste des participants
- `/admin/orders/export` - Export CSV commandes
- `/admin/participants/export` - Export CSV participants
- `/admin/badges/all` - Télécharger tous les badges PDF

## API Endpoints

- `POST /api/validate-promo` - Valider un code promo
- `POST /api/newsletter/subscribe` - Inscription newsletter
- `POST /admin/checkin/<order_number>` - Check-in participant

## Déploiement

### Production avec Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Variables d'environnement en production

```bash
FLASK_ENV=production
SECRET_KEY=votre-secret-key-securisee
DATABASE_URL=postgresql://user:password@localhost/colprad
```

## Sécurité

- HTTPS obligatoire en production
- Validation des entrées utilisateur
- Protection CSRF avec Flask-WTF
- Hashage sécurisé des données sensibles
- Rate limiting recommandé

## Charte Graphique

Le site respecte la charte graphique COLPRAD avec:
- **Palette de couleurs** : Ivoire (#F9F6EF), Turquoise (#0E5E96), Ocre (#D8431A), Bleu nuit (#052B47)
- **Typographie** : Playfair Display (titres) + Inter (corps de texte)
- **Design** : Mobile-first, accessible WCAG AA, contraste optimisé
- **Badges** : Format professionnel 90×135mm avec fond perdu 3mm

Voir `CHARTE_GRAPHIQUE.md` pour plus de détails.

## Badges PDF

Les badges générés incluent:
- **Recto** : Logo, catégorie colorée, nom, organisation, QR code
- **Verso** : Programme, contacts d'urgence, conditions d'accès
- **Couleurs** : VIP (doré), Premium (gris), Standard (blanc), Staff (bleu), Hôtesses (orange), Presse (bordeaux)
- **Format** : 90×135mm portrait + 3mm fond perdu

## Support

Pour toute question ou problème:
- Email: contact@colprad.tg
- Téléphone: +228 XX XX XX XX

## Équipe

- **Responsable COLPRAD** : M. Blaise
- **Développeur** : Daven BANKA

## 📚 Documentation Complète

- **Installation** : Ce fichier (README.md)
- **Structure** : [STRUCTURE_PROJET.md](STRUCTURE_PROJET.md)
- **Déploiement** : [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **Responsive** : [RESPONSIVE_GUIDE.md](RESPONSIVE_GUIDE.md)
- **Charte Graphique** : [CHARTE_GRAPHIQUE.md](CHARTE_GRAPHIQUE.md)
- **Plan de Crise** : [PLAN_COMMUNICATION_CRISE.md](PLAN_COMMUNICATION_CRISE.md)
- **Checklist Finale** : [FINAL_CHECKLIST.md](FINAL_CHECKLIST.md)

## 🎯 Statut du Projet

**Version** : 1.0.0  
**Statut** : ✅ Production Ready  
**Dernière mise à jour** : Janvier 2025

### Fonctionnalités Complétées
- ✅ Site vitrine bilingue (FR/EN)
- ✅ Système de billetterie complet
- ✅ Paiement en ligne (MoovMoney, Mixx By Yas, CB)
- ✅ Génération automatique de QR codes et badges PDF
- ✅ Dashboard administrateur avancé
- ✅ Gestion de crise (alertes, incidents, contacts urgence)
- ✅ Design responsive professionnel
- ✅ Conformité RGPD et légale
- ✅ Performance optimisée
- ✅ Documentation complète

## Licence

© 2025 Life Field Inc. - COLPRAD. Tous droits réservés.

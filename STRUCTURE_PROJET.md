# Structure du Projet COLPRAD

## 📁 Architecture Finale

```
colprad/
├── app.py                          # Application Flask principale (TOUTES LES ROUTES)
├── config.py                       # Configuration
├── models.py                       # Modèles de base de données
├── badge_generator.py              # Génération de badges PDF
├── requirements.txt                # Dépendances Python
├── .env.example                    # Exemple de configuration
├── .gitignore                      # Fichiers à ignorer
├── README.md                       # Documentation principale
│
├── templates/                      # Templates HTML (UNIQUE SOURCE)
│   ├── base.html                   # Template de base
│   ├── index.html                  # Page d'accueil
│   ├── about.html                  # À propos
│   ├── program.html                # Programme
│   ├── speakers.html               # Intervenants
│   ├── tickets.html                # Billetterie
│   ├── order.html                  # Commander
│   ├── checkout.html               # Finaliser commande
│   ├── confirmation.html           # Confirmation
│   ├── practical_info.html         # Infos pratiques
│   ├── contact.html                # Contact
│   ├── press.html                  # Presse
│   ├── cgv.html                    # CGV
│   ├── privacy.html                # Confidentialité
│   ├── legal.html                  # Mentions légales
│   └── admin/                      # Templates admin
│       ├── dashboard.html          # Dashboard
│       ├── participants.html       # Liste participants
│       ├── alerts.html             # Gestion alertes
│       ├── incidents.html          # Gestion incidents
│       └── emergency_contacts.html # Contacts d'urgence
│
├── static/                         # Fichiers statiques
│   ├── css/
│   │   ├── style.css              # Styles principaux
│   │   └── responsive.css         # Styles responsive
│   └── js/
│       ├── main.js                # JavaScript principal
│       └── admin.js               # JavaScript admin
│
└── docs/                          # Documentation
    ├── CHARTE_GRAPHIQUE.md        # Charte graphique
    ├── CGV_COLPRAD.md             # CGV détaillées
    ├── MENTIONS_LEGALES.md        # Mentions légales
    ├── PLAN_COMMUNICATION_CRISE.md # Plan de crise
    ├── CONTACTS_URGENCE_TEMPLATE.md # Template contacts
    ├── RESPONSIVE_GUIDE.md        # Guide responsive
    └── STRUCTURE_PROJET.md        # Ce fichier
```

## 🗂️ Nettoyage Effectué

### Fichiers Supprimés (Doublons)
- ❌ `app/routes.py` → Routes dans `app.py`
- ❌ `app/models.py` → Modèles dans `models.py`
- ❌ `app/config_proxy.py` → Config dans `config.py`
- ❌ `app/__init__.py` → Non nécessaire
- ❌ `app/templates/*.html` → Templates dans `templates/`

### Structure Simplifiée
- ✅ **Un seul fichier de routes** : `app.py`
- ✅ **Un seul dossier templates** : `templates/`
- ✅ **Un seul fichier models** : `models.py`
- ✅ **Un seul fichier config** : `config.py`

## 📋 Routes Disponibles

### Routes Publiques
```python
GET  /                          # Page d'accueil
GET  /about                     # À propos
GET  /program                   # Programme
GET  /speakers                  # Intervenants
GET  /tickets                   # Billetterie
GET  /order                     # Commander
POST /order                     # Traiter commande
GET  /checkout                  # Finaliser
POST /checkout                  # Valider commande
GET  /confirmation/<order_number> # Confirmation
GET  /badge/<order_number>      # Télécharger badge
GET  /practical-info            # Infos pratiques
GET  /contact                   # Contact
POST /contact                   # Envoyer message
GET  /press                     # Presse
GET  /cgv                       # CGV
GET  /privacy                   # Confidentialité
GET  /legal                     # Mentions légales
GET  /set-language/<lang>       # Changer langue
```

### Routes Admin
```python
GET  /admin/dashboard           # Dashboard
GET  /admin/participants        # Liste participants
GET  /admin/orders/export       # Export CSV commandes
GET  /admin/participants/export # Export CSV participants
GET  /admin/badges/all          # Tous les badges PDF
POST /admin/checkin/<order_number> # Check-in
GET  /admin/alerts              # Gestion alertes
POST /admin/alerts/create       # Créer alerte
POST /admin/alerts/<id>/toggle  # Activer/désactiver
POST /admin/alerts/<id>/delete  # Supprimer alerte
GET  /admin/incidents           # Gestion incidents
POST /admin/incidents/create    # Créer incident
POST /admin/incidents/<id>/update # Mettre à jour
GET  /admin/emergency-contacts  # Contacts d'urgence
```

### Routes API
```python
POST /api/validate-promo        # Valider code promo
POST /api/newsletter/subscribe  # Inscription newsletter
```

## 🗄️ Modèles de Base de Données

### Order
- Commandes et billets
- Informations client
- Statut paiement
- Check-in

### PromoCode
- Codes promotionnels
- Réductions
- Limites d'utilisation

### Speaker
- Intervenants
- Biographies (FR/EN)
- Sessions

### ContactMessage
- Messages de contact
- Statut de traitement

### Newsletter
- Inscriptions newsletter
- Statut abonnement

### Alert
- Alertes jour J
- Priorités
- Expiration

### IncidentReport
- Rapports d'incidents
- Sévérité
- Actions prises

## 🎨 Assets Statiques

### CSS
- `style.css` : Styles principaux avec charte graphique
- `responsive.css` : Responsive design complet

### JavaScript
- `main.js` : Fonctionnalités publiques
- `admin.js` : Fonctionnalités admin

## 📚 Documentation

### Guides Techniques
- `README.md` : Installation et utilisation
- `RESPONSIVE_GUIDE.md` : Guide responsive
- `STRUCTURE_PROJET.md` : Architecture

### Documents Légaux
- `CGV_COLPRAD.md` : Conditions générales
- `MENTIONS_LEGALES.md` : Mentions légales
- `CHARTE_GRAPHIQUE.md` : Charte graphique

### Opérationnel
- `PLAN_COMMUNICATION_CRISE.md` : Plan de crise
- `CONTACTS_URGENCE_TEMPLATE.md` : Contacts urgence

## 🚀 Démarrage Rapide

```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Configurer l'environnement
cp .env.example .env
# Éditer .env avec vos paramètres

# 3. Initialiser la base de données
python
>>> from app import app, db
>>> with app.app_context():
...     db.create_all()
>>> exit()

# 4. Lancer l'application
python app.py
```

## 🔧 Maintenance

### Ajouter une Route
1. Ouvrir `app.py`
2. Ajouter la fonction de route
3. Créer le template dans `templates/`
4. Tester

### Ajouter un Modèle
1. Ouvrir `models.py`
2. Créer la classe du modèle
3. Mettre à jour la base de données
4. Utiliser dans les routes

### Modifier le Design
1. Éditer `static/css/style.css` pour styles généraux
2. Éditer `static/css/responsive.css` pour responsive
3. Respecter la charte graphique

### Ajouter du JavaScript
1. Éditer `static/js/main.js` pour fonctionnalités publiques
2. Éditer `static/js/admin.js` pour fonctionnalités admin
3. Tester sur tous les navigateurs

## ✅ Checklist de Déploiement

- [ ] Variables d'environnement configurées
- [ ] Base de données initialisée
- [ ] HTTPS activé
- [ ] Emails configurés
- [ ] Paiements testés
- [ ] Responsive testé
- [ ] Performance optimisée
- [ ] Sécurité vérifiée
- [ ] Backup configuré
- [ ] Monitoring activé

## 📞 Support

- **Développeur** : Daven BANKA
- **Responsable** : M. Blaise
- **Email** : contact@colprad.tg
- **Téléphone** : +228 XX XX XX XX

---

**Dernière mise à jour** : Janvier 2025
**Version** : 1.0.0
**Statut** : Production Ready ✅

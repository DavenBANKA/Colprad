# 🚀 Déploiement sur Render - COLPRAD 2025

## ✅ Guide Complet de Déploiement

Ce guide vous explique comment déployer votre site COLPRAD 2025 sur Render.

---

## 📋 Prérequis

1. ✅ Compte GitHub avec le projet COLPRAD
2. ✅ Compte Render (gratuit) : https://render.com
3. ✅ Clés API PayGate
4. ✅ Compte email pour SMTP

---

## 🚀 Étapes de Déploiement

### 1. Créer un Compte Render

1. Aller sur https://render.com
2. Cliquer sur "Get Started"
3. S'inscrire avec GitHub (recommandé)
4. Autoriser Render à accéder à vos repos

### 2. Créer un Nouveau Web Service

#### Option A : Utiliser render.yaml (Recommandé)

1. Dans le dashboard Render, cliquer sur "New +"
2. Sélectionner "Blueprint"
3. Connecter votre repo GitHub : `DavenBANKA/Colprad`
4. Render détectera automatiquement le fichier `render.yaml`
5. Cliquer sur "Apply"

#### Option B : Configuration Manuelle

1. Dans le dashboard Render, cliquer sur "New +"
2. Sélectionner "Web Service"
3. Connecter votre repo GitHub : `DavenBANKA/Colprad`
4. Configurer :
   - **Name** : `colprad-2025`
   - **Region** : `Frankfurt` (Europe)
   - **Branch** : `main`
   - **Runtime** : `Python 3`
   - **Build Command** : `pip install -r requirements.txt`
   - **Start Command** : `gunicorn app:app`
   - **Plan** : `Free`

### 3. Créer la Base de Données PostgreSQL

1. Dans le dashboard Render, cliquer sur "New +"
2. Sélectionner "PostgreSQL"
3. Configurer :
   - **Name** : `colprad-db`
   - **Database** : `colprad`
   - **User** : `colprad`
   - **Region** : `Frankfurt`
   - **Plan** : `Free`
4. Cliquer sur "Create Database"
5. Copier l'URL de connexion (Internal Database URL)

### 4. Configurer les Variables d'Environnement

Dans les paramètres du Web Service, ajouter les variables :

#### Variables Obligatoires

```env
# Flask
SECRET_KEY=votre-cle-secrete-aleatoire-longue
FLASK_ENV=production

# Database (copier depuis la base de données créée)
DATABASE_URL=postgresql://user:password@host/database

# Email (Gmail recommandé)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=colpradofficiel@gmail.com
MAIL_PASSWORD=votre-mot-de-passe-application
MAIL_DEFAULT_SENDER=colpradofficiel@gmail.com

# PayGate
PAYGATE_API_KEY=votre-cle-api-paygate
PAYGATE_MERCHANT_ID=votre-merchant-id
PAYGATE_WEBHOOK_SECRET=votre-webhook-secret
```

#### Comment Obtenir un Mot de Passe d'Application Gmail

1. Aller sur https://myaccount.google.com/security
2. Activer la validation en 2 étapes
3. Aller dans "Mots de passe des applications"
4. Créer un nouveau mot de passe pour "Mail"
5. Copier le mot de passe généré (16 caractères)

### 5. Initialiser la Base de Données

Une fois le service déployé :

1. Aller dans l'onglet "Shell" du Web Service
2. Exécuter :
```bash
python
>>> from app import app, db
>>> with app.app_context():
...     db.create_all()
>>> exit()
```

Ou créer un script `init_db.py` :
```python
from app import app, db

with app.app_context():
    db.create_all()
    print("Database initialized!")
```

Puis l'exécuter :
```bash
python init_db.py
```

### 6. Configurer le Domaine Personnalisé (Optionnel)

1. Dans les paramètres du Web Service
2. Aller dans "Custom Domain"
3. Ajouter votre domaine : `www.colprad.tg`
4. Suivre les instructions pour configurer les DNS

---

## 🔧 Configuration Avancée

### Fichiers Créés pour Render

#### 1. render.yaml
Configuration automatique du service et de la base de données

#### 2. requirements.txt
Dépendances Python avec `psycopg2-binary` pour PostgreSQL

### Variables d'Environnement Détaillées

| Variable | Description | Exemple |
|----------|-------------|---------|
| `SECRET_KEY` | Clé secrète Flask | `votre-cle-aleatoire-32-caracteres` |
| `DATABASE_URL` | URL PostgreSQL | `postgresql://user:pass@host/db` |
| `FLASK_ENV` | Environnement | `production` |
| `MAIL_SERVER` | Serveur SMTP | `smtp.gmail.com` |
| `MAIL_PORT` | Port SMTP | `587` |
| `MAIL_USE_TLS` | Utiliser TLS | `True` |
| `MAIL_USERNAME` | Email | `colpradofficiel@gmail.com` |
| `MAIL_PASSWORD` | Mot de passe app | `xxxx xxxx xxxx xxxx` |
| `PAYGATE_API_KEY` | Clé API PayGate | `votre-cle-api` |
| `PAYGATE_MERCHANT_ID` | ID Marchand | `votre-merchant-id` |
| `PAYGATE_WEBHOOK_SECRET` | Secret webhook | `votre-secret` |

---

## 🔒 Sécurité

### 1. Générer une SECRET_KEY Sécurisée

```python
import secrets
print(secrets.token_hex(32))
```

Ou en ligne de commande :
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 2. Configurer HTTPS

Render active automatiquement HTTPS avec Let's Encrypt.

### 3. Configurer les URLs PayGate

Dans le dashboard PayGate, mettre à jour les URLs :

- **Success URL** : `https://colprad-2025.onrender.com/payment/success/{order_number}`
- **Cancel URL** : `https://colprad-2025.onrender.com/payment/cancel/{order_number}`
- **Callback URL** : `https://colprad-2025.onrender.com/payment/callback`

---

## 📊 Monitoring

### Logs

1. Dans le dashboard Render
2. Aller dans l'onglet "Logs"
3. Voir les logs en temps réel

### Métriques

1. Dans le dashboard Render
2. Aller dans l'onglet "Metrics"
3. Voir :
   - CPU usage
   - Memory usage
   - Request count
   - Response time

---

## 🔄 Mises à Jour

### Déploiement Automatique

Render redéploie automatiquement à chaque push sur `main` :

```bash
git add .
git commit -m "Update: description"
git push origin main
```

### Déploiement Manuel

1. Dans le dashboard Render
2. Cliquer sur "Manual Deploy"
3. Sélectionner "Deploy latest commit"

---

## 🐛 Dépannage

### Erreur : "Application failed to start"

**Solution** :
1. Vérifier les logs
2. Vérifier que `gunicorn` est dans `requirements.txt`
3. Vérifier la commande de démarrage : `gunicorn app:app`

### Erreur : "Database connection failed"

**Solution** :
1. Vérifier que `DATABASE_URL` est configurée
2. Vérifier que `psycopg2-binary` est dans `requirements.txt`
3. Vérifier que la base de données est créée

### Erreur : "Module not found"

**Solution** :
1. Ajouter le module manquant dans `requirements.txt`
2. Redéployer

### Emails ne sont pas envoyés

**Solution** :
1. Vérifier les variables MAIL_*
2. Utiliser un mot de passe d'application Gmail
3. Vérifier les logs pour les erreurs SMTP

---

## 💰 Plan Gratuit vs Payant

### Plan Gratuit (Free)

**Inclus** :
- ✅ 750 heures/mois
- ✅ HTTPS automatique
- ✅ Déploiement automatique
- ✅ PostgreSQL 1GB
- ⚠️ Le service s'endort après 15 min d'inactivité
- ⚠️ Temps de démarrage : 30-60 secondes

**Limitations** :
- Pas de domaine personnalisé
- Pas de support prioritaire

### Plan Starter ($7/mois)

**Inclus** :
- ✅ Tout du plan gratuit
- ✅ Pas de mise en veille
- ✅ Domaine personnalisé
- ✅ Support prioritaire
- ✅ Plus de ressources

---

## 🎯 Checklist de Déploiement

### Avant le Déploiement
- [x] Code pushé sur GitHub
- [x] `render.yaml` créé
- [x] `requirements.txt` à jour avec `psycopg2-binary`
- [x] `.env.example` à jour
- [ ] Clés PayGate obtenues
- [ ] Compte email configuré

### Pendant le Déploiement
- [ ] Compte Render créé
- [ ] Web Service créé
- [ ] Base de données PostgreSQL créée
- [ ] Variables d'environnement configurées
- [ ] Base de données initialisée

### Après le Déploiement
- [ ] Site accessible
- [ ] Test de réservation
- [ ] Test de paiement (mode test)
- [ ] Test d'email
- [ ] URLs PayGate configurées
- [ ] Domaine personnalisé (optionnel)

---

## 📱 URLs du Site

### URL Render par Défaut
```
https://colprad-2025.onrender.com
```

### URL Personnalisée (après configuration)
```
https://www.colprad.tg
```

---

## 🔗 Liens Utiles

- **Dashboard Render** : https://dashboard.render.com
- **Documentation Render** : https://render.com/docs
- **Support Render** : https://render.com/support
- **Status Render** : https://status.render.com

---

## 💡 Conseils

### 1. Utiliser le Plan Gratuit pour Tester

Commencez avec le plan gratuit pour tester, puis passez au plan payant avant l'événement.

### 2. Surveiller les Logs

Vérifiez régulièrement les logs pour détecter les erreurs.

### 3. Backup de la Base de Données

Exportez régulièrement les données :
```bash
# Dans le shell Render
python
>>> from app import Order
>>> orders = Order.query.all()
>>> # Exporter en CSV
```

### 4. Tester en Mode Test

Testez tout en mode test avant de passer en production.

---

## 🎉 Félicitations !

Votre site COLPRAD 2025 est maintenant déployé sur Render ! 🚀

### Prochaines Étapes

1. ✅ Tester toutes les fonctionnalités
2. ✅ Configurer PayGate en production
3. ✅ Tester les paiements
4. ✅ Communiquer l'URL
5. ✅ Surveiller les réservations

---

## 📞 Support

### Problèmes de Déploiement
- Email : blaisederge@outlook.com
- Téléphone : +228 92 53 05 12

### Support Render
- Documentation : https://render.com/docs
- Community : https://community.render.com

---

**Date de création** : 11 Décembre 2025
**Version** : 1.0
**Status** : ✅ Prêt pour le Déploiement

**Bon déploiement ! 🚀**

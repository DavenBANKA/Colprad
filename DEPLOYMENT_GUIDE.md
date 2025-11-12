# Guide de Déploiement - COLPRAD

## 🚀 Déploiement en Production

### Prérequis

- Python 3.8+
- PostgreSQL (recommandé pour production)
- Serveur web (Nginx/Apache)
- Certificat SSL
- Nom de domaine configuré

## 📋 Étapes de Déploiement

### 1. Préparation du Serveur

```bash
# Mise à jour du système
sudo apt update && sudo apt upgrade -y

# Installation des dépendances
sudo apt install python3-pip python3-venv nginx postgresql postgresql-contrib -y

# Installation de certbot pour SSL
sudo apt install certbot python3-certbot-nginx -y
```

### 2. Configuration PostgreSQL

```bash
# Connexion à PostgreSQL
sudo -u postgres psql

# Création de la base de données
CREATE DATABASE colprad_db;
CREATE USER colprad_user WITH PASSWORD 'votre_mot_de_passe_securise';
GRANT ALL PRIVILEGES ON DATABASE colprad_db TO colprad_user;
\q
```

### 3. Déploiement de l'Application

```bash
# Création du répertoire
sudo mkdir -p /var/www/colprad
cd /var/www/colprad

# Clone du projet (ou upload via FTP/SCP)
git clone <repository-url> .

# Création de l'environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installation des dépendances
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

### 4. Configuration de l'Environnement

```bash
# Création du fichier .env
nano .env
```

Contenu du `.env` pour production :

```env
# Flask
FLASK_APP=app.py
FLASK_ENV=production
SECRET_KEY=votre_cle_secrete_tres_longue_et_aleatoire

# Database
DATABASE_URL=postgresql://colprad_user:votre_mot_de_passe@localhost/colprad_db

# Email
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=noreply@colprad.tg
MAIL_PASSWORD=votre_mot_de_passe_email
MAIL_DEFAULT_SENDER=noreply@colprad.tg

# PayGate
PAYGATE_API_KEY=votre_cle_api_paygate
PAYGATE_MERCHANT_ID=votre_merchant_id
PAYGATE_WEBHOOK_SECRET=votre_webhook_secret

# Google Analytics
GA_TRACKING_ID=UA-XXXXXXXXX-X
```

### 5. Initialisation de la Base de Données

```bash
# Activation de l'environnement virtuel
source venv/bin/activate

# Initialisation
python3
>>> from app import app, db
>>> with app.app_context():
...     db.create_all()
>>> exit()
```

### 6. Configuration de Gunicorn

Créer `/etc/systemd/system/colprad.service` :

```ini
[Unit]
Description=Gunicorn instance for COLPRAD
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/colprad
Environment="PATH=/var/www/colprad/venv/bin"
ExecStart=/var/www/colprad/venv/bin/gunicorn --workers 4 --bind unix:colprad.sock -m 007 app:app

[Install]
WantedBy=multi-user.target
```

Démarrer le service :

```bash
sudo systemctl start colprad
sudo systemctl enable colprad
sudo systemctl status colprad
```

### 7. Configuration Nginx

Créer `/etc/nginx/sites-available/colprad` :

```nginx
server {
    listen 80;
    server_name colprad.tg www.colprad.tg;

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/colprad/colprad.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /var/www/colprad/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/json;

    client_max_body_size 10M;
}
```

Activer le site :

```bash
sudo ln -s /etc/nginx/sites-available/colprad /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 8. Configuration SSL avec Let's Encrypt

```bash
sudo certbot --nginx -d colprad.tg -d www.colprad.tg
```

Renouvellement automatique :

```bash
sudo certbot renew --dry-run
```

### 9. Configuration du Firewall

```bash
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable
sudo ufw status
```

## 🔒 Sécurité

### 1. Permissions des Fichiers

```bash
sudo chown -R www-data:www-data /var/www/colprad
sudo chmod -R 755 /var/www/colprad
sudo chmod 600 /var/www/colprad/.env
```

### 2. Configuration PostgreSQL Sécurisée

```bash
# Éditer pg_hba.conf
sudo nano /etc/postgresql/*/main/pg_hba.conf

# Changer 'peer' en 'md5' pour les connexions locales
local   all             all                                     md5
```

### 3. Fail2Ban (Protection contre les attaques)

```bash
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 4. Backup Automatique

Créer `/usr/local/bin/backup_colprad.sh` :

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/colprad"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup base de données
pg_dump -U colprad_user colprad_db > $BACKUP_DIR/db_$DATE.sql

# Backup fichiers
tar -czf $BACKUP_DIR/files_$DATE.tar.gz /var/www/colprad

# Garder seulement les 7 derniers backups
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

Rendre exécutable et ajouter au cron :

```bash
sudo chmod +x /usr/local/bin/backup_colprad.sh
sudo crontab -e

# Ajouter : Backup quotidien à 2h du matin
0 2 * * * /usr/local/bin/backup_colprad.sh
```

## 📊 Monitoring

### 1. Logs

```bash
# Logs Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Logs Gunicorn
sudo journalctl -u colprad -f

# Logs PostgreSQL
sudo tail -f /var/log/postgresql/postgresql-*.log
```

### 2. Monitoring des Performances

Installer et configurer :

```bash
# Monitoring système
sudo apt install htop iotop -y

# Monitoring PostgreSQL
sudo apt install postgresql-contrib -y
```

### 3. Uptime Monitoring

Utiliser des services comme :
- UptimeRobot (gratuit)
- Pingdom
- StatusCake

## 🔄 Mise à Jour

### Procédure de Mise à Jour

```bash
# 1. Backup
/usr/local/bin/backup_colprad.sh

# 2. Arrêter le service
sudo systemctl stop colprad

# 3. Mettre à jour le code
cd /var/www/colprad
git pull origin main

# 4. Activer l'environnement virtuel
source venv/bin/activate

# 5. Mettre à jour les dépendances
pip install -r requirements.txt --upgrade

# 6. Migrations de base de données (si nécessaire)
python3
>>> from app import app, db
>>> with app.app_context():
...     db.create_all()
>>> exit()

# 7. Redémarrer le service
sudo systemctl start colprad
sudo systemctl status colprad

# 8. Vérifier les logs
sudo journalctl -u colprad -n 50
```

## 🧪 Tests Post-Déploiement

### Checklist

- [ ] Site accessible via HTTPS
- [ ] Redirection HTTP → HTTPS fonctionne
- [ ] Toutes les pages se chargent
- [ ] Formulaires fonctionnent
- [ ] Paiements testés (mode test)
- [ ] Emails envoyés correctement
- [ ] QR codes générés
- [ ] Badges PDF téléchargeables
- [ ] Dashboard admin accessible
- [ ] Export CSV fonctionne
- [ ] Responsive sur mobile
- [ ] Performance acceptable (< 3s)
- [ ] SSL valide (A+ sur SSL Labs)
- [ ] Backups fonctionnent

### Tests de Charge

```bash
# Installer Apache Bench
sudo apt install apache2-utils -y

# Test de charge
ab -n 1000 -c 10 https://colprad.tg/
```

## 🚨 Dépannage

### Service ne démarre pas

```bash
# Vérifier les logs
sudo journalctl -u colprad -n 100

# Vérifier les permissions
ls -la /var/www/colprad

# Tester manuellement
cd /var/www/colprad
source venv/bin/activate
gunicorn --bind 0.0.0.0:8000 app:app
```

### Erreur 502 Bad Gateway

```bash
# Vérifier que Gunicorn tourne
sudo systemctl status colprad

# Vérifier le socket
ls -la /var/www/colprad/colprad.sock

# Redémarrer Nginx
sudo systemctl restart nginx
```

### Base de données inaccessible

```bash
# Vérifier PostgreSQL
sudo systemctl status postgresql

# Tester la connexion
psql -U colprad_user -d colprad_db -h localhost
```

## 📱 Configuration Mobile

### PWA (Progressive Web App)

Ajouter `manifest.json` et service worker pour une expérience mobile optimale.

### Push Notifications

Configurer Firebase Cloud Messaging pour les notifications push.

## 🌍 CDN et Performance

### Cloudflare (Recommandé)

1. Créer un compte Cloudflare
2. Ajouter le domaine colprad.tg
3. Changer les nameservers
4. Activer :
   - SSL/TLS Full
   - Auto Minify (CSS, JS, HTML)
   - Brotli compression
   - Caching

### Optimisation Images

```bash
# Installer ImageMagick
sudo apt install imagemagick -y

# Optimiser les images
find static/images -name "*.jpg" -exec convert {} -quality 85 {} \;
find static/images -name "*.png" -exec optipng {} \;
```

## 📞 Support

### Contacts Techniques

- **Développeur** : Daven BANKA
- **Email** : dev@colprad.tg
- **Urgence** : +228 XX XX XX XX

### Documentation

- Guide utilisateur : `/docs/user-guide.pdf`
- API Documentation : `/docs/api.md`
- Troubleshooting : `/docs/troubleshooting.md`

---

**Dernière mise à jour** : Janvier 2025
**Version** : 1.0.0
**Statut** : Production Ready ✅

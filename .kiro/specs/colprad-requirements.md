# COLPRAD - Spécifications Techniques

## Vue d'ensemble
Site de billetterie en ligne pour le Colloque des Professionnels de l'Art pour le Développement (COLPRAD) avec Flask.

## Stack Technique
- Backend: Python Flask
- Base de données: SQLite (dev) / PostgreSQL (prod)
- Frontend: HTML5, CSS3, JavaScript, Bootstrap 5
- Paiement: PayGate (MoovMoney, Mixx By Yas, CB)
- Email: Flask-Mail
- QR Code: qrcode library

## Fonctionnalités Principales

### 1. Billetterie
- Types: Standard, Premium, VIP, Gratuit
- Gestion quotas par type
- Codes promo/remises
- Génération QR code + email confirmation
- Export CSV commandes
- Dashboard temps réel
- Check-in mobile via QR

### 2. Site Vitrine (Bilingue FR/EN)
- Accueil
- À propos
- Programme
- Intervenants
- Billetterie
- Infos pratiques
- Contact
- Presse/Partenaires

### 3. Parcours Achat (3 étapes max)
- Sélection billet → Coordonnées → Paiement → Confirmation

### 4. Badges
- Catégories: VIP (doré #D4AF37), Premium (gris #9E9E9E), Standard (blanc), Staff (bleu #0057A6), Hôtesses (orange #FF7F11)
- Format: 90×135mm, QR code, infos participant

## Critères d'Acceptation
- Achat complet < 5 min
- Email confirmation < 60s avec QR
- Export CSV conforme
- Page accueil < 3s (mobile 3G)
- Responsive mobile-first
- WCAG AA

## Délai
Mise en ligne: 10/11/2025

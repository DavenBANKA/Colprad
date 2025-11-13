# Système de QR Code - COLPRAD 2025

## 🎯 Fonctionnement

Le système de QR Code est entièrement automatisé et professionnel. Voici comment il fonctionne :

---

## 📧 Envoi Automatique du QR Code

### Quand le QR Code est-il envoyé ?

Le QR Code est **automatiquement généré et envoyé par email** dans les cas suivants :

1. **Après un paiement réussi** (route `/retour-paiement`)
   - Le client est redirigé depuis PayGate avec status = "completed"
   - Le QR Code est généré immédiatement
   - L'email de confirmation est envoyé avec le QR Code

2. **Via le webhook PayGate** (route `/payment/webhook`)
   - PayGate envoie une notification de paiement réussi
   - Si l'email n'a pas déjà été envoyé, le système l'envoie
   - Double sécurité pour garantir la réception

---

## 🔢 Format du QR Code

Le QR Code contient les informations suivantes :

```
COLPRAD2025|ORD-20241113-001|client@email.com
```

**Structure :**
- `COLPRAD2025` : Identifiant de l'événement
- `ORD-20241113-001` : Numéro de commande unique
- `client@email.com` : Email du participant

---

## 📨 Contenu de l'Email de Confirmation

L'email envoyé au client contient :

### 1. En-tête Professionnel
- Logo et titre COLPRAD 2025
- Design avec dégradé de couleurs

### 2. Détails de la Réservation
- ✅ Numéro de commande
- ✅ Type de billet (STANDARD, PREMIUM, VIP)
- ✅ Quantité
- ✅ Montant payé
- ✅ Date : 13 Décembre 2025
- ✅ Horaires : 14H00 - 17H00
- ✅ Lieu : Hôtel Elie Palace, Adidogomé - Lomé

### 3. QR Code Visible
- **Image du QR Code** (300x300px)
- Numéro de commande en grand
- Instructions claires : "Présentez ce QR code à l'entrée"

### 4. Instructions Importantes
- Arriver 30 minutes avant (13H30)
- Pièce d'identité requise
- Tenue professionnelle recommandée
- QR code imprimé ou sur smartphone

### 5. Contacts d'Urgence
- Email : colpradofficiel@gmail.com
- Téléphone : +228 92 38 40 92
- WhatsApp : +228 92 38 40 92

---

## 🖨️ Options pour le Client

Le client peut utiliser son QR Code de plusieurs façons :

### Option 1 : Smartphone
- Ouvrir l'email sur le téléphone
- Afficher le QR Code à l'entrée
- ✅ Recommandé : Simple et rapide

### Option 2 : Impression
- Imprimer l'email complet
- Présenter le QR Code imprimé
- ✅ Recommandé pour les billets VIP

### Option 3 : Badge PDF
- Télécharger le badge depuis la page de confirmation
- Imprimer le badge professionnel
- ✅ Recommandé pour networking

### Option 4 : Numéro de Commande
- Si problème avec le QR Code
- Présenter le numéro de commande
- L'équipe peut retrouver la réservation

---

## 🔍 Vérification à l'Entrée

### Processus de Check-in

1. **Scan du QR Code**
   - L'équipe scanne le QR Code
   - Le système vérifie la validité
   - Affiche les informations du participant

2. **Vérification Manuelle**
   - Si le QR Code ne fonctionne pas
   - Recherche par numéro de commande
   - Recherche par nom/email

3. **Validation**
   - Marquer comme "checked-in" dans la base de données
   - Enregistrer l'heure d'arrivée
   - Remettre le badge physique

---

## 🛡️ Sécurité

### Mesures de Sécurité Implémentées

1. **QR Code Unique**
   - Chaque commande a un QR Code unique
   - Impossible de dupliquer

2. **Vérification en Base de Données**
   - Le QR Code est vérifié contre la base de données
   - Détecte les tentatives de fraude

3. **Check-in Unique**
   - Une fois scanné, le billet est marqué comme utilisé
   - Empêche la réutilisation

4. **Logs d'Audit**
   - Tous les scans sont enregistrés
   - Traçabilité complète

---

## 📊 Statistiques et Suivi

### Informations Disponibles

- Nombre total de billets vendus
- Nombre de participants arrivés (checked-in)
- Heure d'arrivée de chaque participant
- Type de billet par participant
- Taux de présence en temps réel

---

## 🔧 Administration

### Routes Admin pour la Gestion

1. **Dashboard** : `/admin/dashboard`
   - Vue d'ensemble des ventes
   - Statistiques en temps réel

2. **Liste des Participants** : `/admin/participants`
   - Tous les participants
   - Statut de check-in
   - Export CSV

3. **Check-in Manuel** : `/admin/checkin/<order_number>`
   - Marquer un participant comme arrivé
   - En cas de problème technique

4. **Télécharger Badges** : `/admin/badges/all`
   - Télécharger tous les badges en PDF
   - Pour impression en masse

---

## 📱 Exemple d'Email Reçu

```
De: COLPRAD 2025 <noreply@colprad.com>
À: client@email.com
Objet: ✅ Confirmation COLPRAD 2025 - Billet STANDARD - Réf ORD-20241113-001

[En-tête avec logo et couleurs]

🎉 Réservation Confirmée !

Bonjour Jean Dupont,

Merci pour votre réservation ! Nous sommes ravis de vous compter 
parmi les participants du COLPRAD 2025.

📋 Détails de votre réservation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Numéro de commande : ORD-20241113-001
Type de billet : STANDARD
Quantité : 1
Montant payé : 5,000 FCFA
Date de l'événement : 13 Décembre 2025
Horaires : 14H00 - 17H00
Lieu : Hôtel Elie Palace, Adidogomé - Lomé

📱 Votre QR Code d'Accès
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
IMPORTANT : Présentez ce QR code à l'entrée le jour de l'événement

[IMAGE DU QR CODE - 300x300px]

ORD-20241113-001
Vous pouvez également présenter ce numéro de commande

⚠️ À ne pas oublier le jour J :
• Présentez votre QR code (imprimé ou sur smartphone)
• Arrivez 30 minutes avant le début (dès 13H30)
• Munissez-vous d'une pièce d'identité
• Tenue professionnelle recommandée

Besoin d'aide ?
📧 Email : colpradofficiel@gmail.com
📱 Téléphone : +228 92 38 40 92
💬 WhatsApp : +228 92 38 40 92

[Footer avec informations de l'événement]
```

---

## ✅ Checklist Client

Pour le participant, voici ce qu'il doit faire :

- [ ] Vérifier la réception de l'email de confirmation
- [ ] Vérifier que le QR Code est visible dans l'email
- [ ] Sauvegarder l'email ou l'imprimer
- [ ] Télécharger le badge PDF (optionnel)
- [ ] Arriver à 13H30 le 13 Décembre 2025
- [ ] Avoir son QR Code prêt (smartphone ou imprimé)
- [ ] Avoir une pièce d'identité

---

## 🆘 En Cas de Problème

### Le client n'a pas reçu l'email ?

1. Vérifier les spams/courrier indésirable
2. Vérifier l'adresse email utilisée lors de la commande
3. Contacter le support : colpradofficiel@gmail.com
4. Fournir le numéro de commande

### Le QR Code ne s'affiche pas ?

1. Ouvrir l'email dans un autre client email
2. Télécharger le badge PDF depuis la page de confirmation
3. Utiliser le numéro de commande à la place
4. Contacter le support

### Le QR Code ne fonctionne pas à l'entrée ?

1. Présenter le numéro de commande
2. L'équipe peut faire une recherche manuelle
3. Vérification par nom et email
4. Check-in manuel possible

---

## 📞 Support Technique

Pour toute question sur le système de QR Code :

- **Email** : colpradofficiel@gmail.com
- **Téléphone** : +228 92 38 40 92
- **WhatsApp** : https://wa.me/22892384092
- **Disponibilité** : 7 jours sur 7

---

**Date de mise à jour** : 13 Novembre 2024  
**Version** : 2.0.0  
**Statut** : ✅ Système opérationnel et testé

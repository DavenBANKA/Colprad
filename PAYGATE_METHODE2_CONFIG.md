# Configuration PayGate - Méthode 2 (Redirection Simple)

## 🎯 Configuration Appliquée

Le système de paiement COLPRAD 2025 utilise maintenant la **Méthode 2 de PayGate** : Redirection Simple.

### Avantages de cette méthode
- ✅ Plus simple à implémenter
- ✅ Pas besoin de shop_id/merchant_id
- ✅ Redirection directe vers PayGate
- ✅ Retour automatique après paiement

---

## 🔧 Configuration dans `.env`

```env
# Email Configuration
MAIL_USERNAME=colpradofficiel@gmail.com
MAIL_PASSWORD=d7h13@05#92
MAIL_DEFAULT_SENDER=noreply@colprad.com

# PayGate Configuration (Méthode 2 - Redirection)
PAYGATE_API_KEY=376cd4f8-7fff-4ba3-ba3a-e73444632857
PAYGATE_WEBHOOK_SECRET=dev_test_secret
PAYGATE_PAYMENT_RETURN_URL=http://localhost:5000/payment/return
```

### En Production (Render)

```env
PAYGATE_PAYMENT_RETURN_URL=https://votre-domaine.com/payment/return
```

---

## 📋 Paramètres Envoyés à PayGate

Lors de la redirection vers PayGate, les paramètres suivants sont envoyés :

| Paramètre | Description | Exemple |
|-----------|-------------|---------|
| `token` | Votre clé API PayGate | 376cd4f8-7fff-4ba3-ba3a-e73444632857 |
| `amount` | Montant en FCFA | 5000 |
| `description` | Description de la transaction | COLPRAD 2025 - Billet STANDARD - Commande ORD-20241113-001 |
| `identifier` | Numéro de commande unique | ORD-20241113-001 |
| `url` | URL de retour après paiement | http://localhost:5000/payment/return |

---

## 🔄 Flux de Paiement

```
1. Utilisateur clique sur "Confirmer et payer"
   ↓
2. Création de la commande en base de données (status: pending)
   ↓
3. Redirection vers /process-payment/<order_number>
   ↓
4. Préparation des paramètres PayGate
   ↓
5. Affichage de la page de redirection (payment_redirect.html)
   ↓
6. Auto-submit du formulaire vers PayGate (2 secondes)
   ↓
7. PayGate affiche la page de paiement
   ↓
8. Utilisateur effectue le paiement
   ↓
9. PayGate redirige vers PAYGATE_PAYMENT_RETURN_URL avec paramètres:
   - identifier: Numéro de commande
   - transaction_id: ID de la transaction PayGate
   - status: completed/cancelled/failed
   ↓
10. Route /payment/return traite le retour:
    - Si status = completed → Confirmation + Email + QR Code
    - Si status = cancelled → Retour à /tickets
    - Si status = failed → Retour à /tickets avec erreur
```

---

## 🧪 Test de la Configuration

### 1. Vérifier la Configuration

```bash
# Démarrer Flask
python app.py

# Ouvrir dans le navigateur
http://localhost:5000/test-paygate
```

Cette page affiche :
- ✅/❌ PAYGATE_API_KEY (token)
- ✅/❌ PAYGATE_WEBHOOK_SECRET
- ✅/❌ PAYGATE_PAYMENT_RETURN_URL
- ✅/❌ Configuration Email

### 2. Tester une Commande

1. Allez sur http://localhost:5000/tickets
2. Sélectionnez un billet (Standard: 5000 FCFA, Premium: 15000 FCFA, VIP: 50000 FCFA)
3. Cliquez sur "Réserver"
4. Remplissez le formulaire de checkout
5. Cliquez sur "Confirmer et payer"
6. Vous devriez voir la page de redirection
7. Après 2 secondes, redirection automatique vers PayGate

### 3. Vérifier la Console

Dans la console du navigateur (F12), vous devriez voir :
```
Submitting payment form to PayGate...
```

---

## 📥 Paramètres de Retour PayGate

Après le paiement, PayGate redirige vers votre URL de retour avec ces paramètres :

### Paiement Réussi
```
http://localhost:5000/payment/return?identifier=ORD-20241113-001&transaction_id=TXN123456&status=completed
```

### Paiement Annulé
```
http://localhost:5000/payment/return?identifier=ORD-20241113-001&status=cancelled
```

### Paiement Échoué
```
http://localhost:5000/payment/return?identifier=ORD-20241113-001&status=failed
```

---

## 🔔 Webhook PayGate (Optionnel)

En plus du retour utilisateur, PayGate peut envoyer une notification webhook à :

```
POST https://votre-domaine.com/payment/webhook
```

### Headers
```
X-Webhook-Secret: dev_test_secret
Content-Type: application/json
```

### Body
```json
{
  "identifier": "ORD-20241113-001",
  "transaction_id": "TXN123456",
  "status": "completed",
  "amount": 5000,
  "currency": "XOF"
}
```

Le webhook permet de :
- Confirmer le paiement même si l'utilisateur ferme le navigateur
- Avoir une double vérification du paiement
- Envoyer l'email de confirmation si pas déjà envoyé

---

## 🐛 Dépannage

### Problème : "Le système de paiement n'est pas configuré"

**Cause** : PAYGATE_API_KEY manquant dans `.env`

**Solution** :
1. Vérifiez que `.env` contient `PAYGATE_API_KEY=376cd4f8-7fff-4ba3-ba3a-e73444632857`
2. Redémarrez Flask
3. Testez avec `/test-paygate`

### Problème : La redirection ne fonctionne pas

**Cause** : JavaScript bloqué ou erreur de formulaire

**Solution** :
1. Ouvrez la console (F12)
2. Cherchez les erreurs
3. Cliquez manuellement sur "Continuer vers le paiement"

### Problème : Retour de paiement ne fonctionne pas

**Cause** : URL de retour incorrecte

**Solution** :
1. Vérifiez `PAYGATE_PAYMENT_RETURN_URL` dans `.env`
2. En local : `http://localhost:5000/payment/return`
3. En production : `https://votre-domaine.com/payment/return`

### Problème : Email de confirmation non reçu

**Cause** : Configuration email incorrecte

**Solution** :
1. Vérifiez `MAIL_USERNAME` et `MAIL_PASSWORD` dans `.env`
2. Vérifiez les logs Flask pour les erreurs d'envoi
3. Testez l'envoi d'email manuellement

---

## 🚀 Déploiement sur Render

### Variables d'Environnement

Dans Render Dashboard > Environment, ajoutez :

```
FLASK_ENV=production
SECRET_KEY=votre-secret-key-production-tres-securisee
DATABASE_URL=postgresql://...

# Email
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=colpradofficiel@gmail.com
MAIL_PASSWORD=d7h13@05#92
MAIL_DEFAULT_SENDER=noreply@colprad.com

# PayGate
PAYGATE_API_KEY=376cd4f8-7fff-4ba3-ba3a-e73444632857
PAYGATE_WEBHOOK_SECRET=production_webhook_secret_change_me
PAYGATE_PAYMENT_RETURN_URL=https://votre-domaine.com/payment/return
```

### Configuration PayGate Dashboard

Si PayGate nécessite une configuration de webhook :

1. Connectez-vous à https://paygate.tg
2. Allez dans Paramètres > Webhooks
3. Ajoutez l'URL : `https://votre-domaine.com/payment/webhook`
4. Secret : Utilisez la valeur de `PAYGATE_WEBHOOK_SECRET`

---

## 📊 Statuts de Commande

| Statut | Description | Action |
|--------|-------------|--------|
| `pending` | Commande créée, paiement en attente | Redirection vers PayGate |
| `completed` | Paiement réussi | Email + QR Code envoyés |
| `cancelled` | Paiement annulé par l'utilisateur | Peut réessayer |
| `failed` | Paiement échoué | Peut réessayer |

---

## ✅ Checklist de Vérification

Avant de considérer le système opérationnel :

- [ ] `PAYGATE_API_KEY` configuré dans `.env`
- [ ] `PAYGATE_WEBHOOK_SECRET` configuré dans `.env`
- [ ] `PAYGATE_PAYMENT_RETURN_URL` configuré dans `.env`
- [ ] Configuration email testée
- [ ] Page `/test-paygate` affiche tout en vert
- [ ] Test de commande complète réussi
- [ ] Redirection vers PayGate fonctionnelle
- [ ] Retour après paiement fonctionnel
- [ ] Email de confirmation reçu
- [ ] QR code généré correctement
- [ ] Page de confirmation affichée

---

## 📞 Support

### Contacts COLPRAD
- **Email** : colpradofficiel@gmail.com
- **Téléphone** : +228 92 38 40 92
- **WhatsApp** : https://wa.me/22892384092

### Support PayGate
- **Email** : support@paygate.tg
- **Documentation** : https://docs.paygate.tg
- **Dashboard** : https://paygate.tg

---

## 🔐 Sécurité

### Points de Sécurité Implémentés

✅ Vérification de la configuration avant redirection  
✅ Validation du webhook secret  
✅ Identifiant unique par commande  
✅ HTTPS obligatoire en production  
✅ Pas d'exposition des clés dans le frontend  

### Bonnes Pratiques

- ❌ Ne jamais commiter le fichier `.env`
- ✅ Utiliser des secrets différents en dev et prod
- ✅ Vérifier le webhook secret sur chaque notification
- ✅ Logger toutes les transactions pour audit
- ✅ Envoyer l'email de confirmation uniquement après vérification

---

**Date de configuration** : 13 Novembre 2024  
**Version** : 2.0.0 - Méthode 2 PayGate  
**Statut** : ✅ Configuré et prêt à tester

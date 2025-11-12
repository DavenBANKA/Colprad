# 💳 Intégration PayGate - COLPRAD 2025

## ✅ Système de Paiement Configuré

Le système de paiement avec PayGate est maintenant **entièrement intégré** au site COLPRAD 2025.

---

## 🔄 Flux de Paiement

### 1. Sélection du Billet
L'utilisateur choisit son type de billet (Standard, Premium ou VIP)

### 2. Formulaire de Commande
L'utilisateur remplit ses informations :
- Prénom et Nom
- Email
- Téléphone
- Organisation (optionnel)
- Code promo (optionnel)

### 3. Redirection vers PayGate
- La commande est créée avec le statut "pending"
- L'utilisateur est redirigé vers PayGate
- PayGate affiche les options de paiement :
  - MoovMoney
  - Mixx By Yas
  - Carte bancaire

### 4. Paiement sur PayGate
L'utilisateur effectue le paiement de manière sécurisée sur PayGate

### 5. Retour et Confirmation
- **Succès** : Redirection vers la page de confirmation
- **Annulation** : Retour à la page billetterie
- **Callback** : PayGate notifie le serveur du statut

### 6. Email de Confirmation
- Email automatique avec QR code
- Détails de la commande
- Instructions pour l'événement

---

## 📁 Fichiers Modifiés

### 1. app.py ✅
**Nouvelles routes ajoutées :**

```python
@app.route('/process-payment/<order_number>')
def process_payment(order_number):
    # Prépare les paramètres PayGate
    # Redirige vers PayGate
    
@app.route('/payment/success/<order_number>')
def payment_success(order_number):
    # Met à jour le statut : completed
    # Envoie l'email de confirmation
    
@app.route('/payment/cancel/<order_number>')
def payment_cancel(order_number):
    # Met à jour le statut : cancelled
    # Redirige vers billetterie
    
@app.route('/payment/callback', methods=['POST'])
def payment_callback():
    # Webhook PayGate
    # Met à jour le statut automatiquement
```

**Modifications :**
- Route `/checkout` modifiée pour créer la commande avec statut "pending"
- Redirection vers `/process-payment` au lieu de confirmation directe

### 2. templates/payment_redirect.html ✅
**Nouveau template créé :**
- Page de transition vers PayGate
- Formulaire auto-submit après 2 secondes
- Affichage du numéro de commande et montant
- Spinner de chargement

---

## 🔧 Configuration PayGate

### 1. Obtenir les Clés API

**Étapes :**
1. Créer un compte sur https://www.paygate.tg
2. Accéder au tableau de bord
3. Obtenir :
   - `API Key` (auth_token)
   - `Merchant ID` (shop_id)
   - `Webhook Secret`

### 2. Configurer les Variables d'Environnement

Créer un fichier `.env` à la racine du projet :

```bash
cp .env.example .env
```

Éditer `.env` avec vos clés PayGate :

```env
# PayGate Configuration
PAYGATE_API_KEY=votre-cle-api-paygate
PAYGATE_MERCHANT_ID=votre-merchant-id
PAYGATE_WEBHOOK_SECRET=votre-webhook-secret
```

### 3. Configurer les URLs de Callback

Dans le tableau de bord PayGate, configurer :

**URL de Succès :**
```
https://votre-domaine.com/payment/success/{order_number}
```

**URL d'Annulation :**
```
https://votre-domaine.com/payment/cancel/{order_number}
```

**URL de Callback (Webhook) :**
```
https://votre-domaine.com/payment/callback
```

---

## 📊 Paramètres Envoyés à PayGate

```python
{
    'auth_token': 'votre-cle-api',
    'shop_id': 'votre-merchant-id',
    'amount': 5000,  # Montant en FCFA
    'currency': 'XOF',  # Franc CFA
    'description': 'COLPRAD 2025 - Billet STANDARD',
    'custom_field': 'COLPRAD-2025-XXXXX',  # Numéro de commande
    'customer_name': 'Jean Dupont',
    'customer_email': 'jean@example.com',
    'customer_phone': '+22890000000',
    'success_url': 'https://...',
    'cancel_url': 'https://...',
    'callback_url': 'https://...'
}
```

---

## 🔔 Webhook PayGate

### Format de la Réponse

PayGate envoie une requête POST au callback_url :

```json
{
    "transaction_id": "TXN123456789",
    "custom_field": "COLPRAD-2025-XXXXX",
    "status": "successful",
    "amount": 5000,
    "currency": "XOF",
    "payment_method": "momo",
    "customer_email": "jean@example.com"
}
```

### Statuts Possibles

| Statut | Description |
|--------|-------------|
| `successful` | Paiement réussi |
| `completed` | Paiement complété |
| `failed` | Paiement échoué |
| `pending` | En attente |
| `cancelled` | Annulé par l'utilisateur |

---

## 🔒 Sécurité

### 1. Vérification du Webhook

Le webhook vérifie :
- Le `custom_field` (numéro de commande)
- Le `transaction_id`
- Le `status`

### 2. Protection CSRF

Les formulaires utilisent les tokens CSRF de Flask

### 3. HTTPS Obligatoire

En production, toutes les URLs doivent être en HTTPS

### 4. Validation des Montants

Le montant est vérifié côté serveur avant et après le paiement

---

## 🧪 Tests

### Mode Test PayGate

PayGate propose un mode test avec des cartes de test :

**Carte de Test Succès :**
```
Numéro : 4111 1111 1111 1111
CVV : 123
Date : 12/25
```

**Carte de Test Échec :**
```
Numéro : 4000 0000 0000 0002
CVV : 123
Date : 12/25
```

### Tester le Flux Complet

1. Aller sur `/tickets`
2. Sélectionner un billet
3. Remplir le formulaire
4. Vérifier la redirection vers PayGate
5. Effectuer un paiement test
6. Vérifier la confirmation et l'email

---

## 📧 Email de Confirmation

Après un paiement réussi, l'utilisateur reçoit :

### Contenu de l'Email
- Numéro de commande
- Type de billet
- Montant payé
- QR Code unique
- Informations de l'événement
- Instructions d'accès

### QR Code
Format : `COLPRAD2025|{order_number}|{email}`

---

## 🎫 Statuts de Commande

| Statut | Description | Action |
|--------|-------------|--------|
| `pending` | En attente de paiement | Créé après formulaire |
| `completed` | Paiement réussi | Email envoyé |
| `failed` | Paiement échoué | Peut réessayer |
| `cancelled` | Annulé par l'utilisateur | Peut recommencer |

---

## 📱 Méthodes de Paiement

PayGate supporte :

### 1. MoovMoney
- Paiement mobile
- Instantané
- Populaire au Togo

### 2. Mixx By Yas
- Paiement mobile
- Alternative locale

### 3. Carte Bancaire
- Visa
- Mastercard
- Paiement international

---

## 🔍 Suivi des Paiements

### Dans l'Admin

Accéder à `/admin/dashboard` pour voir :
- Total des commandes
- Revenus totaux
- Commandes par type
- Statuts des paiements

### Export des Données

Exporter les commandes en CSV :
```
/admin/orders/export
```

---

## ⚠️ Gestion des Erreurs

### Paiement Échoué
- Message d'erreur affiché
- Possibilité de réessayer
- Commande conservée avec statut "failed"

### Timeout
- Redirection automatique après 15 minutes
- Statut "cancelled"

### Webhook Non Reçu
- Vérifier les logs PayGate
- Vérifier l'URL du webhook
- Vérifier que le serveur est accessible

---

## 📊 Monitoring

### Logs à Surveiller

1. **Créations de commandes**
   - Nombre par jour
   - Types de billets

2. **Redirections PayGate**
   - Taux de succès
   - Temps de réponse

3. **Callbacks reçus**
   - Statuts
   - Délais

4. **Emails envoyés**
   - Taux de délivrance
   - Erreurs

---

## 🚀 Mise en Production

### Checklist

- [ ] Obtenir les clés API PayGate production
- [ ] Configurer les variables d'environnement
- [ ] Configurer les URLs de callback
- [ ] Tester avec une vraie carte
- [ ] Vérifier la réception des emails
- [ ] Vérifier les webhooks
- [ ] Activer HTTPS
- [ ] Tester le flux complet

### URLs de Production

Remplacer dans `app.py` :
```python
paygate_url = "https://www.paygate.tg/v1/page"  # Production
```

---

## 💡 Conseils

### 1. Tester Régulièrement
Effectuer des tests de paiement réguliers

### 2. Surveiller les Webhooks
Vérifier que tous les webhooks sont reçus

### 3. Backup des Commandes
Exporter régulièrement les données

### 4. Support Client
Préparer des réponses pour les problèmes courants

---

## 📞 Support PayGate

### Contact
- Email : support@paygate.tg
- Téléphone : [À compléter]
- Documentation : https://docs.paygate.tg

### Problèmes Courants

**Webhook non reçu :**
- Vérifier l'URL configurée
- Vérifier que le serveur est accessible
- Vérifier les logs PayGate

**Paiement bloqué :**
- Vérifier les clés API
- Vérifier le montant minimum
- Contacter le support PayGate

---

## ✅ Résumé

### Ce Qui a Été Fait

1. ✅ Intégration complète de PayGate
2. ✅ Redirection automatique vers PayGate
3. ✅ Gestion des callbacks (webhooks)
4. ✅ Pages de succès et d'annulation
5. ✅ Envoi automatique des emails
6. ✅ Génération des QR codes
7. ✅ Suivi des statuts de paiement

### Prochaines Étapes

1. Obtenir les clés API PayGate
2. Configurer le fichier .env
3. Tester en mode test
4. Déployer en production
5. Surveiller les paiements

---

**Date de création :** 11 Décembre 2025
**Version :** 1.0
**Status :** ✅ Intégration Complète

**Le système de paiement PayGate est prêt ! 💳**

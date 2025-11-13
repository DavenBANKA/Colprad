# Configuration PayGate pour COLPRAD 2025

## 🔧 Problème Identifié

Le système de paiement ne redirige pas correctement vers PayGate car les paramètres de configuration ne sont pas complets.

## ✅ Solution

### 1. Compléter le fichier `.env`

Vous devez obtenir vos vraies clés PayGate et mettre à jour le fichier `.env` :

```env
# PayGate Configuration
PAYGATE_API_KEY=8b2d7abf-1df9-409e-a1f3-52ebea6e3deb
PAYGATE_MERCHANT_ID=VOTRE_MERCHANT_ID_ICI
PAYGATE_WEBHOOK_SECRET=VOTRE_WEBHOOK_SECRET_ICI
```

### 2. Obtenir vos Clés PayGate

Pour obtenir vos clés PayGate :

1. **Connectez-vous à votre compte PayGate** : https://www.paygate.tg
2. **Accédez à votre tableau de bord marchand**
3. **Trouvez vos identifiants** :
   - `PAYGATE_API_KEY` : Clé API (auth_token) ✅ Déjà configurée
   - `PAYGATE_MERCHANT_ID` : ID de votre boutique (shop_id) ⚠️ À configurer
   - `PAYGATE_WEBHOOK_SECRET` : Secret pour valider les webhooks ⚠️ À configurer

### 3. Configuration des URLs de Retour

Dans votre compte PayGate, configurez les URLs de retour :

- **URL de succès** : `https://votre-domaine.com/payment/success/<order_number>`
- **URL d'annulation** : `https://votre-domaine.com/payment/cancel/<order_number>`
- **URL de callback (webhook)** : `https://votre-domaine.com/payment/callback`

## 🧪 Test du Système de Paiement

### Mode Test (Développement)

1. **Vérifier que les clés sont chargées** :
   ```python
   # Dans app.py ou console Python
   from config import Config
   print(f"API Key: {Config.PAYGATE_API_KEY}")
   print(f"Merchant ID: {Config.PAYGATE_MERCHANT_ID}")
   ```

2. **Tester une commande** :
   - Allez sur `/tickets`
   - Sélectionnez un billet
   - Remplissez le formulaire
   - Cliquez sur "Confirmer et payer"
   - Vous devriez être redirigé vers PayGate

### Vérification des Logs

Si la redirection ne fonctionne pas, vérifiez :

1. **Console du navigateur** (F12) :
   - Cherchez les erreurs JavaScript
   - Vérifiez que le formulaire se soumet

2. **Logs Flask** :
   ```bash
   # Dans votre terminal où Flask tourne
   # Vous devriez voir :
   # "Submitting payment form to PayGate..."
   ```

## 🔍 Diagnostic des Problèmes

### Problème 1 : "Le système de paiement n'est pas configuré"

**Cause** : Les clés PayGate ne sont pas dans le fichier `.env`

**Solution** :
1. Vérifiez que le fichier `.env` existe
2. Vérifiez que les variables sont bien définies
3. Redémarrez Flask après modification du `.env`

### Problème 2 : La page de redirection s'affiche mais ne redirige pas

**Cause** : JavaScript bloqué ou erreur de formulaire

**Solution** :
1. Ouvrez la console du navigateur (F12)
2. Cliquez manuellement sur "Continuer vers le paiement"
3. Vérifiez les erreurs dans la console

### Problème 3 : Erreur PayGate "Invalid credentials"

**Cause** : Clés PayGate incorrectes

**Solution** :
1. Vérifiez vos clés dans le dashboard PayGate
2. Assurez-vous d'utiliser les clés du bon environnement (test/production)
3. Mettez à jour le `.env` avec les bonnes clés

### Problème 4 : Le paiement réussit mais pas de confirmation

**Cause** : Webhook non configuré ou email non envoyé

**Solution** :
1. Vérifiez la configuration email dans `.env`
2. Vérifiez que l'URL de callback est accessible publiquement
3. Consultez les logs Flask pour voir si le webhook est reçu

## 📝 Checklist de Configuration

- [ ] `PAYGATE_API_KEY` configuré dans `.env`
- [ ] `PAYGATE_MERCHANT_ID` configuré dans `.env`
- [ ] `PAYGATE_WEBHOOK_SECRET` configuré dans `.env`
- [ ] URLs de retour configurées dans PayGate
- [ ] Email configuré pour les confirmations
- [ ] Test d'une commande complète
- [ ] Vérification de la réception du webhook
- [ ] Vérification de l'envoi de l'email de confirmation

## 🚀 Mise en Production

Avant de déployer sur Render :

1. **Variables d'environnement sur Render** :
   - Allez dans votre service Render
   - Section "Environment"
   - Ajoutez toutes les variables du `.env`

2. **URLs de production** :
   - Mettez à jour les URLs de callback dans PayGate
   - Utilisez votre domaine de production

3. **Mode production** :
   ```env
   FLASK_ENV=production
   ```

## 📞 Support

Si vous rencontrez des problèmes :

1. **Support PayGate** : support@paygate.tg
2. **Documentation PayGate** : https://docs.paygate.tg
3. **Vérifiez les logs** : Consultez les logs Flask et les logs PayGate

## 🔐 Sécurité

⚠️ **IMPORTANT** :
- Ne commitez JAMAIS le fichier `.env` sur Git
- Gardez vos clés secrètes
- Utilisez des clés de test en développement
- Utilisez des clés de production uniquement en production

---

**Dernière mise à jour** : 13 Novembre 2024

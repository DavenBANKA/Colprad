from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, send_file
from flask_mail import Mail, Message
from config import Config
from models import db, Order, PromoCode, Speaker, ContactMessage, Newsletter, Alert, IncidentReport
import qrcode
from io import BytesIO
import base64
import csv
from datetime import datetime, timedelta
from badge_generator import generate_badge_pdf, generate_multiple_badges_pdf

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
mail = Mail(app)

# Language support and alerts
@app.context_processor
def inject_language():
    lang = session.get('lang', app.config['DEFAULT_LANGUAGE'])
    # Get active alerts
    active_alerts = Alert.query.filter_by(active=True).order_by(Alert.priority.desc(), Alert.created_at.desc()).all()
    active_alerts = [a for a in active_alerts if a.is_active()]
    return dict(current_lang=lang, active_alerts=active_alerts)

@app.route('/set-language/<lang>')
def set_language(lang):
    if lang in app.config['SUPPORTED_LANGUAGES']:
        session['lang'] = lang
    return redirect(request.referrer or url_for('index'))

# Main routes
@app.route('/')
def index():
    lang = session.get('lang', 'fr')
    return render_template('index.html', lang=lang)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/program')
def program():
    return render_template('program.html')

@app.route('/speakers')
def speakers():
    speakers_list = Speaker.query.order_by(Speaker.order_index).all()
    return render_template('speakers.html', speakers=speakers_list)

@app.route('/practical-info')
def practical_info():
    return render_template('practical_info.html')

@app.route('/press')
def press():
    return render_template('press.html')

@app.route('/cgv')
def cgv():
    return render_template('cgv.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/legal')
def legal():
    return render_template('legal.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        contact_msg = ContactMessage(
            name=name,
            email=email,
            subject=subject,
            message=message
        )
        db.session.add(contact_msg)
        db.session.commit()
        
        flash('Votre message a été envoyé avec succès!', 'success')
        return redirect(url_for('contact'))
    
    return render_template('contact.html')

# Ticketing routes
@app.route('/tickets')
def tickets():
    ticket_types = app.config['TICKET_TYPES']
    return render_template('tickets.html', ticket_types=ticket_types)

@app.route('/order', methods=['GET', 'POST'])
def order():
    if request.method == 'POST':
        ticket_type = request.form.get('ticket_type')
        quantity = int(request.form.get('quantity', 1))
        
        if ticket_type not in app.config['TICKET_TYPES']:
            flash('Type de billet invalide', 'error')
            return redirect(url_for('tickets'))
        
        ticket_info = app.config['TICKET_TYPES'][ticket_type]
        unit_price = ticket_info['price']
        total = unit_price * quantity
        
        session['order_data'] = {
            'ticket_type': ticket_type,
            'quantity': quantity,
            'unit_price': unit_price,
            'total': total
        }
        
        return redirect(url_for('checkout'))
    
    ticket_type = request.args.get('type', 'standard')
    quantity = request.args.get('quantity', 1)
    return render_template('order.html', ticket_type=ticket_type, quantity=quantity)

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    order_data = session.get('order_data')
    if not order_data:
        return redirect(url_for('tickets'))
    
    if request.method == 'POST':
        order = Order(
            ticket_type=order_data['ticket_type'],
            quantity=order_data['quantity'],
            unit_price=order_data['unit_price'],
            total_amount=order_data['total'],
            first_name=request.form.get('first_name'),
            last_name=request.form.get('last_name'),
            email=request.form.get('email'),
            phone=request.form.get('phone'),
            organization=request.form.get('organization'),
            payment_method=request.form.get('payment_method'),
            payment_status='pending'
        )
        
        promo_code = request.form.get('promo_code')
        if promo_code:
            promo = PromoCode.query.filter_by(code=promo_code, active=True).first()
            if promo and (not promo.max_uses or promo.uses_count < promo.max_uses):
                if promo.discount_type == 'percentage':
                    discount = order.total_amount * (promo.discount_value / 100)
                else:
                    discount = promo.discount_value
                order.discount_amount = discount
                order.total_amount -= discount
                order.promo_code = promo_code
                promo.uses_count += 1
        
        db.session.add(order)
        db.session.commit()
        
        # Redirect to PayGate for payment
        return redirect(url_for('process_payment', order_number=order.order_number))
    
    return render_template('checkout.html', order_data=order_data)

@app.route('/process-payment/<order_number>')
def process_payment(order_number):
    order = Order.query.filter_by(order_number=order_number).first_or_404()
    
    # Check if PayGate is properly configured
    if not app.config.get('PAYGATE_API_KEY'):
        flash('Le système de paiement n\'est pas configuré. Contactez l\'administrateur.', 'error')
        return redirect(url_for('tickets'))
    
    # PayGate configuration (Méthode 2 - Redirection simple)
    paygate_url = "https://paygate.tg/checkout"
    
    # Prepare PayGate parameters
    paygate_params = {
        'token': app.config['PAYGATE_API_KEY'],
        'amount': int(order.total_amount),
        'description': f'COLPRAD 2025 - Billet {order.ticket_type.upper()} - Commande {order.order_number}',
        'identifier': order.order_number,
        'url': app.config.get('PAYGATE_PAYMENT_RETURN_URL') or url_for('payment_return', _external=True)
    }
    
    return render_template('payment_redirect.html', 
                         paygate_url=paygate_url, 
                         paygate_params=paygate_params,
                         order=order)

@app.route('/retour-paiement')
def retour_paiement():
    """
    Route de retour après paiement PayGate (Méthode 2)
    PayGate redirige ici avec les paramètres: identifier, transaction_id, status
    """
    order_number = request.args.get('identifier') or request.args.get('order_number')
    transaction_id = request.args.get('transaction_id') or request.args.get('tx_reference')
    status = request.args.get('status') or request.args.get('payment_status')
    
    # Log pour débogage
    print(f"=== RETOUR PAIEMENT ===")
    print(f"Order Number: {order_number}")
    print(f"Transaction ID: {transaction_id}")
    print(f"Status: {status}")
    print(f"All params: {request.args}")
    
    if not order_number:
        flash('Commande introuvable. Vérifiez votre email pour la confirmation.', 'warning')
        return redirect(url_for('tickets'))
    
    order = Order.query.filter_by(order_number=order_number).first()
    
    if not order:
        flash('Commande introuvable. Contactez le support si vous avez effectué un paiement.', 'error')
        return redirect(url_for('tickets'))
    
    # Vérifier le statut du paiement
    if status in ['completed', 'successful', 'success', 'paid']:
        # Paiement réussi
        if order.payment_status != 'completed':
            order.payment_status = 'completed'
            order.payment_reference = transaction_id or 'PAYGATE-' + order.order_number
            db.session.commit()
            
            # Generate QR code
            qr_data = f"COLPRAD2025|{order.order_number}|{order.email}"
            qr_code = generate_qr_code(qr_data)
            
            # Send confirmation email
            try:
                send_confirmation_email(order, qr_code)
            except Exception as e:
                print(f"Erreur envoi email: {e}")
        
        session.pop('order_data', None)
        flash('Paiement effectué avec succès ! Consultez votre email pour la confirmation.', 'success')
        return redirect(url_for('confirmation', order_number=order.order_number))
    
    elif status in ['cancelled', 'canceled', 'cancel']:
        # Paiement annulé
        order.payment_status = 'cancelled'
        db.session.commit()
        flash('Paiement annulé. Vous pouvez réessayer quand vous voulez.', 'warning')
        return redirect(url_for('tickets'))
    
    elif status in ['failed', 'error', 'declined']:
        # Paiement échoué
        order.payment_status = 'failed'
        db.session.commit()
        flash('Le paiement a échoué. Veuillez vérifier vos informations et réessayer.', 'error')
        return redirect(url_for('tickets'))
    
    elif status in ['pending', 'processing']:
        # Paiement en cours
        flash('Votre paiement est en cours de traitement. Vous recevrez une confirmation par email.', 'info')
        return redirect(url_for('confirmation', order_number=order.order_number))
    
    else:
        # Statut inconnu - on affiche quand même la confirmation
        print(f"Statut inconnu: {status}")
        flash('Paiement en cours de vérification. Consultez votre email pour la confirmation.', 'info')
        return redirect(url_for('confirmation', order_number=order.order_number))

@app.route('/payment/webhook', methods=['POST'])
def payment_webhook():
    """
    Webhook PayGate pour notifications de paiement
    """
    data = request.json or request.form.to_dict()
    
    # Vérifier le secret webhook
    webhook_secret = request.headers.get('X-Webhook-Secret')
    if webhook_secret != app.config.get('PAYGATE_WEBHOOK_SECRET'):
        return jsonify({'error': 'Invalid webhook secret'}), 403
    
    order_number = data.get('identifier')
    transaction_id = data.get('transaction_id')
    status = data.get('status')
    
    if order_number:
        order = Order.query.filter_by(order_number=order_number).first()
        if order:
            if status == 'successful' or status == 'completed':
                order.payment_status = 'completed'
                order.payment_reference = transaction_id
                
                # Generate and send confirmation if not already sent
                if order.payment_status != 'completed':
                    qr_data = f"COLPRAD2025|{order.order_number}|{order.email}"
                    qr_code = generate_qr_code(qr_data)
                    send_confirmation_email(order, qr_code)
            elif status == 'failed':
                order.payment_status = 'failed'
            elif status == 'cancelled':
                order.payment_status = 'cancelled'
            
            db.session.commit()
    
    return jsonify({'status': 'ok'}), 200

@app.route('/confirmation/<order_number>')
def confirmation(order_number):
    order = Order.query.filter_by(order_number=order_number).first_or_404()
    qr_data = f"COLPRAD2025|{order.order_number}|{order.email}"
    qr_code = generate_qr_code(qr_data)
    return render_template('confirmation.html', order=order, qr_code=qr_code)

# Admin routes
@app.route('/admin/dashboard')
def admin_dashboard():
    total_orders = Order.query.count()
    total_revenue = db.session.query(db.func.sum(Order.total_amount)).filter(
        Order.payment_status == 'completed'
    ).scalar() or 0
    
    orders_by_type = db.session.query(
        Order.ticket_type,
        db.func.count(Order.id),
        db.func.sum(Order.quantity)
    ).group_by(Order.ticket_type).all()
    
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
    
    return render_template('admin/dashboard.html',
                         total_orders=total_orders,
                         total_revenue=total_revenue,
                         orders_by_type=orders_by_type,
                         recent_orders=recent_orders)

@app.route('/admin/orders/export')
def export_orders():
    orders = Order.query.all()
    
    output = BytesIO()
    output.write('\ufeff'.encode('utf-8'))  # BOM for Excel
    
    writer = csv.writer(output)
    writer.writerow(['id_commande', 'date_commande', 'type_billet', 'quantite',
                    'montant_total', 'statut_paiement', 'prenom', 'nom',
                    'email', 'telephone', 'code_promo', 'reference_paiement'])
    
    for order in orders:
        writer.writerow([
            order.order_number,
            order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            order.ticket_type,
            order.quantity,
            order.total_amount,
            order.payment_status,
            order.first_name,
            order.last_name,
            order.email,
            order.phone,
            order.promo_code or '',
            order.payment_reference or ''
        ])
    
    output.seek(0)
    return output.getvalue(), 200, {
        'Content-Type': 'text/csv; charset=utf-8',
        'Content-Disposition': f'attachment; filename=colprad_orders_{datetime.now().strftime("%Y%m%d")}.csv'
    }

@app.route('/admin/checkin/<order_number>', methods=['POST'])
def checkin(order_number):
    order = Order.query.filter_by(order_number=order_number).first_or_404()
    order.checked_in = True
    order.check_in_time = datetime.utcnow()
    db.session.commit()
    return jsonify({'success': True, 'message': 'Check-in réussi'})

@app.route('/badge/<order_number>')
def download_badge(order_number):
    order = Order.query.filter_by(order_number=order_number).first_or_404()
    
    # Generate badge PDF
    pdf_buffer = generate_badge_pdf(order)
    
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'badge_colprad_{order_number}.pdf'
    )

@app.route('/admin/badges/all')
def download_all_badges():
    orders = Order.query.filter_by(payment_status='completed').all()
    
    if not orders:
        flash('Aucune commande confirmée', 'warning')
        return redirect(url_for('admin_dashboard'))
    
    # Generate all badges
    pdf_buffer = generate_multiple_badges_pdf(orders)
    
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'badges_colprad_{datetime.now().strftime("%Y%m%d")}.pdf'
    )

@app.route('/admin/participants')
def participants_list():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('admin/participants.html', orders=orders)

@app.route('/admin/alerts')
def admin_alerts():
    alerts = Alert.query.order_by(Alert.created_at.desc()).all()
    return render_template('admin/alerts.html', alerts=alerts)

@app.route('/admin/alerts/create', methods=['POST'])
def create_alert():
    title = request.form.get('title')
    message = request.form.get('message')
    alert_type = request.form.get('alert_type', 'info')
    priority = int(request.form.get('priority', 0))
    expires_hours = request.form.get('expires_hours')
    
    alert = Alert(
        title=title,
        message=message,
        alert_type=alert_type,
        priority=priority,
        created_by='Admin'
    )
    
    if expires_hours:
        from datetime import timedelta
        alert.expires_at = datetime.utcnow() + timedelta(hours=int(expires_hours))
    
    db.session.add(alert)
    db.session.commit()
    
    # Send email to all participants if urgent
    if priority >= 2:
        send_urgent_alert_email(alert)
    
    flash('Alerte créée avec succès', 'success')
    return redirect(url_for('admin_alerts'))

@app.route('/admin/alerts/<int:alert_id>/toggle', methods=['POST'])
def toggle_alert(alert_id):
    alert = Alert.query.get_or_404(alert_id)
    alert.active = not alert.active
    db.session.commit()
    return jsonify({'success': True, 'active': alert.active})

@app.route('/admin/alerts/<int:alert_id>/delete', methods=['POST'])
def delete_alert(alert_id):
    alert = Alert.query.get_or_404(alert_id)
    db.session.delete(alert)
    db.session.commit()
    flash('Alerte supprimée', 'success')
    return redirect(url_for('admin_alerts'))

@app.route('/admin/incidents')
def admin_incidents():
    incidents = IncidentReport.query.order_by(IncidentReport.created_at.desc()).all()
    return render_template('admin/incidents.html', incidents=incidents)

@app.route('/admin/incidents/create', methods=['POST'])
def create_incident():
    incident = IncidentReport(
        incident_type=request.form.get('incident_type'),
        severity=request.form.get('severity'),
        title=request.form.get('title'),
        description=request.form.get('description'),
        location=request.form.get('location'),
        reported_by=request.form.get('reported_by', 'Admin')
    )
    
    db.session.add(incident)
    db.session.commit()
    
    flash('Incident enregistré', 'success')
    return redirect(url_for('admin_incidents'))

@app.route('/admin/incidents/<int:incident_id>/update', methods=['POST'])
def update_incident(incident_id):
    incident = IncidentReport.query.get_or_404(incident_id)
    
    incident.status = request.form.get('status', incident.status)
    incident.actions_taken = request.form.get('actions_taken')
    incident.impact_assessment = request.form.get('impact_assessment')
    
    if incident.status in ['resolved', 'closed'] and not incident.resolved_at:
        incident.resolved_at = datetime.utcnow()
        incident.resolved_by = 'Admin'
    
    db.session.commit()
    
    flash('Incident mis à jour', 'success')
    return redirect(url_for('admin_incidents'))

@app.route('/admin/emergency-contacts')
def emergency_contacts():
    return render_template('admin/emergency_contacts.html')

@app.route('/admin/participants/export')
def export_participants():
    orders = Order.query.all()
    
    output = BytesIO()
    output.write('\ufeff'.encode('utf-8'))
    
    writer = csv.writer(output)
    writer.writerow(['N°', 'Nom complet', 'Organisation', 'Rôle', 'Catégorie', 
                    'N° billet', 'Paiement', 'Contact', 'ID', 'Remarques', 
                    'Check-in', 'Heure arrivée'])
    
    for idx, order in enumerate(orders, 1):
        writer.writerow([
            idx,
            f"{order.first_name} {order.last_name}",
            order.organization or '',
            '',  # Rôle - à compléter manuellement
            order.ticket_type.upper(),
            f"{order.id:04d}",
            order.payment_method or '',
            f"{order.email} / {order.phone}",
            '',  # ID - à compléter manuellement
            '',  # Remarques
            'Oui' if order.checked_in else 'Non',
            order.check_in_time.strftime('%Y-%m-%d %H:%M:%S') if order.check_in_time else ''
        ])
    
    output.seek(0)
    return output.getvalue(), 200, {
        'Content-Type': 'text/csv; charset=utf-8',
        'Content-Disposition': f'attachment; filename=participants_colprad_{datetime.now().strftime("%Y%m%d")}.csv'
    }

# Test payment simulation (for development only)
@app.route('/test-payment/<order_number>')
def test_payment(order_number):
    """
    Page de test pour simuler un retour PayGate
    À SUPPRIMER EN PRODUCTION !
    """
    order = Order.query.filter_by(order_number=order_number).first_or_404()
    
    return f"""
    <html>
    <head>
        <title>Test Paiement - COLPRAD</title>
        <style>
            body {{ font-family: Arial, sans-serif; padding: 40px; background: #f5f5f5; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }}
            h1 {{ color: #D8431A; }}
            .btn {{ display: inline-block; padding: 12px 24px; margin: 10px; text-decoration: none; border-radius: 5px; color: white; font-weight: bold; }}
            .success {{ background: #28a745; }}
            .warning {{ background: #ffc107; color: #000; }}
            .danger {{ background: #dc3545; }}
            .info {{ background: #17a2b8; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🧪 Test Paiement</h1>
            <p><strong>Commande:</strong> {order.order_number}</p>
            <p><strong>Montant:</strong> {order.total_amount:,.0f} FCFA</p>
            <p><strong>Client:</strong> {order.first_name} {order.last_name}</p>
            
            <h3>Simuler un retour PayGate:</h3>
            
            <a href="/retour-paiement?identifier={order.order_number}&transaction_id=TEST-TXN-{order.order_number}&status=completed" class="btn success">
                ✅ Paiement Réussi
            </a>
            
            <a href="/retour-paiement?identifier={order.order_number}&status=cancelled" class="btn warning">
                ⚠️ Paiement Annulé
            </a>
            
            <a href="/retour-paiement?identifier={order.order_number}&status=failed" class="btn danger">
                ❌ Paiement Échoué
            </a>
            
            <a href="/retour-paiement?identifier={order.order_number}&status=pending" class="btn info">
                ⏳ Paiement En Cours
            </a>
            
            <hr>
            <p><small>⚠️ Cette page est pour les tests uniquement. À supprimer en production !</small></p>
        </div>
    </body>
    </html>
    """

# Test route for PayGate configuration
@app.route('/test-paygate')
def test_paygate():
    api_key_configured = '✅ Configuré' if app.config.get('PAYGATE_API_KEY') else '❌ Manquant'
    webhook_configured = '✅ Configuré' if app.config.get('PAYGATE_WEBHOOK_SECRET') else '❌ Manquant'
    return_url_configured = '✅ Configuré' if app.config.get('PAYGATE_PAYMENT_RETURN_URL') else '❌ Manquant'
    mail_configured = '✅ Configuré' if app.config.get('MAIL_USERNAME') else '❌ Manquant'
    
    api_key_value = app.config.get('PAYGATE_API_KEY', 'Non défini')
    if api_key_value != 'Non défini':
        api_key_value = api_key_value[:20] + '...'
    
    return_url_value = app.config.get('PAYGATE_PAYMENT_RETURN_URL', 'Non défini')
    
    all_configured = (api_key_configured == '✅ Configuré' and 
                     webhook_configured == '✅ Configuré' and 
                     return_url_configured == '✅ Configuré')
    
    html = """
    <html>
    <head>
        <title>Test Configuration PayGate</title>
        <style>
            body {{ font-family: Arial, sans-serif; padding: 40px; background: #f5f5f5; }}
            .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            h1 {{ color: #D8431A; }}
            .status {{ padding: 15px; margin: 10px 0; border-radius: 5px; }}
            .success {{ background: #d4edda; border-left: 4px solid #28a745; }}
            .error {{ background: #f8d7da; border-left: 4px solid #dc3545; }}
            .info {{ background: #d1ecf1; border-left: 4px solid #0c5460; padding: 15px; margin: 20px 0; border-radius: 5px; }}
            code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 3px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔧 Test Configuration PayGate - COLPRAD 2025</h1>
            
            <h2>État de la Configuration</h2>
            
            <div class="status {0}">
                <strong>PAYGATE_API_KEY (token):</strong> {1}<br>
                <small>Valeur: {2}</small>
            </div>
            
            <div class="status {3}">
                <strong>PAYGATE_WEBHOOK_SECRET:</strong> {4}
            </div>
            
            <div class="status {5}">
                <strong>PAYGATE_PAYMENT_RETURN_URL:</strong> {6}<br>
                <small>Valeur: {7}</small>
            </div>
            
            <div class="status {8}">
                <strong>Configuration Email:</strong> {9}
            </div>
            
            <div class="info">
                <h3>ℹ️ Méthode PayGate</h3>
                <p><strong>Méthode 2 - Redirection Simple</strong></p>
                <p>Cette configuration utilise la redirection simple PayGate avec:</p>
                <ul>
                    <li><code>token</code>: Votre clé API PayGate</li>
                    <li><code>amount</code>: Montant en FCFA</li>
                    <li><code>description</code>: Description de la transaction</li>
                    <li><code>identifier</code>: Numéro de commande</li>
                    <li><code>url</code>: URL de retour après paiement</li>
                </ul>
            </div>
            
            <div class="info">
                <h3>📋 Actions Requises</h3>
                {10}
            </div>
            
            <h3>🧪 Test de Paiement</h3>
            <p>
                <a href="/tickets" style="display: inline-block; background: #D8431A; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin-right: 10px;">
                    Tester une Commande
                </a>
                <a href="/" style="display: inline-block; background: #0057A6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px;">
                    Retour à l'Accueil
                </a>
            </p>
            
            <div class="info">
                <h3>📞 Besoin d'Aide ?</h3>
                <p>Consultez le fichier <code>CONFIGURATION_PAYGATE.md</code> pour un guide complet de configuration.</p>
            </div>
        </div>
    </body>
    </html>
    """.format(
        'success' if api_key_configured == '✅ Configuré' else 'error',
        api_key_configured,
        api_key_value,
        'success' if webhook_configured == '✅ Configuré' else 'error',
        webhook_configured,
        'success' if return_url_configured == '✅ Configuré' else 'error',
        return_url_configured,
        return_url_value,
        'success' if mail_configured == '✅ Configuré' else 'error',
        mail_configured,
        '<p>✅ Toutes les configurations sont en place ! Vous pouvez tester le paiement.</p>' if all_configured else '''
                <p>⚠️ Configuration incomplète. Veuillez :</p>
                <ol>
                    <li>Ouvrir le fichier <code>.env</code></li>
                    <li>Compléter les valeurs manquantes</li>
                    <li>Redémarrer Flask</li>
                    <li>Rafraîchir cette page</li>
                </ol>
                <p>Consultez <code>CONFIGURATION_PAYGATE.md</code> pour plus de détails.</p>
        '''
    )
    
    return html

# API routes
@app.route('/api/validate-promo', methods=['POST'])
def validate_promo():
    code = request.json.get('code')
    promo = PromoCode.query.filter_by(code=code, active=True).first()
    
    if not promo:
        return jsonify({'valid': False, 'message': 'Code promo invalide'})
    
    if promo.max_uses and promo.uses_count >= promo.max_uses:
        return jsonify({'valid': False, 'message': 'Code promo expiré'})
    
    return jsonify({
        'valid': True,
        'discount_type': promo.discount_type,
        'discount_value': promo.discount_value
    })

@app.route('/api/newsletter/subscribe', methods=['POST'])
def subscribe_newsletter():
    email = request.json.get('email')
    
    existing = Newsletter.query.filter_by(email=email).first()
    if existing:
        return jsonify({'success': False, 'message': 'Email déjà inscrit'})
    
    newsletter = Newsletter(email=email)
    db.session.add(newsletter)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Inscription réussie'})

# Utility functions
def generate_qr_code(data):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"

def send_confirmation_email(order, qr_code):
    subject = f"Confirmation de votre réservation COLPRAD — Réf {order.order_number}"
    
    html_body = f"""
    <html>
    <body>
        <h2>Bonjour {order.first_name} {order.last_name},</h2>
        <p>Merci pour votre réservation pour COLPRAD 2025.</p>
        <p>Votre commande <strong>{order.order_number}</strong> a bien été enregistrée.</p>
        
        <h3>Détails :</h3>
        <ul>
            <li>Type de billet : {order.ticket_type.upper()}</li>
            <li>Quantité : {order.quantity}</li>
            <li>Montant : {order.total_amount} FCFA</li>
        </ul>
        
        <p>Présentez ce QR code ou ce numéro à l'accueil le jour J.</p>
        <img src="{qr_code}" alt="QR Code" />
        
        <p>En cas de question : contact@colprad.tg / +228 XX XX XX XX</p>
        <p>Cordialement,<br>L'équipe COLPRAD</p>
    </body>
    </html>
    """
    
    msg = Message(subject, recipients=[order.email], html=html_body)
    mail.send(msg)

def send_urgent_alert_email(alert):
    """Send urgent alert to all participants"""
    orders = Order.query.filter_by(payment_status='completed').all()
    emails = list(set([order.email for order in orders]))
    
    subject = f"URGENT — COLPRAD : {alert.title}"
    
    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif;">
        <div style="background-color: #D8431A; color: white; padding: 20px; text-align: center;">
            <h2>⚠️ ALERTE IMPORTANTE</h2>
        </div>
        <div style="padding: 20px;">
            <h3>{alert.title}</h3>
            <p>{alert.message}</p>
            
            <p style="margin-top: 30px;">
                Pour plus d'informations : <a href="https://colprad.tg">colprad.tg</a><br>
                Contact d'urgence : +228 XX XX XX XX
            </p>
            
            <p style="color: #666; font-size: 12px; margin-top: 30px;">
                Ceci est un message automatique de l'équipe COLPRAD.
            </p>
        </div>
    </body>
    </html>
    """
    
    # Send in batches to avoid overwhelming the mail server
    batch_size = 50
    for i in range(0, len(emails), batch_size):
        batch = emails[i:i+batch_size]
        msg = Message(subject, recipients=batch, html=html_body)
        try:
            mail.send(msg)
        except Exception as e:
            print(f"Error sending alert email: {e}")

# Initialize database
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)

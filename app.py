from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, send_file
from flask_mail import Mail, Message
from config import Config
from models import db, Order, PromoCode, Speaker, ContactMessage, Newsletter, Alert, IncidentReport
import qrcode
from io import BytesIO
import base64
import csv
from datetime import datetime
from badge_generator import generate_badge_pdf, generate_multiple_badges_pdf
import logging

app = Flask(__name__)
app.config.from_object(Config)

# Configuration du logging professionnel
if app.config['FLASK_ENV'] == 'production':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler('colprad.log'),
            logging.StreamHandler()
        ]
    )
else:
    logging.basicConfig(level=logging.DEBUG)

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
    """
    Prépare et redirige vers la page de paiement PayGate
    """
    order = Order.query.filter_by(order_number=order_number).first_or_404()
    
    # Vérification de sécurité : la commande doit être en attente
    if order.payment_status == 'completed':
        flash('Cette commande a déjà été payée.', 'info')
        return redirect(url_for('confirmation', order_number=order.order_number))
    
    # Vérification de la configuration PayGate
    if not app.config.get('PAYGATE_API_KEY'):
        app.logger.error('PAYGATE_API_KEY non configuré')
        flash('Le système de paiement est temporairement indisponible. Veuillez réessayer plus tard.', 'error')
        return redirect(url_for('contact'))
    
    if not app.config.get('PAYGATE_PAYMENT_RETURN_URL'):
        app.logger.error('PAYGATE_PAYMENT_RETURN_URL non configuré')
        flash('Le système de paiement est temporairement indisponible. Veuillez réessayer plus tard.', 'error')
        return redirect(url_for('contact'))
    
    # PayGate configuration (Méthode 2 - Redirection simple)
    paygate_url = "https://paygate.tg/checkout"
    
    # Préparation des paramètres PayGate
    paygate_params = {
        'token': app.config['PAYGATE_API_KEY'],
        'amount': int(order.total_amount),
        'description': f'COLPRAD 2025 - Billet {order.ticket_type.upper()} - {order.first_name} {order.last_name}',
        'identifier': order.order_number,
        'url': app.config['PAYGATE_PAYMENT_RETURN_URL']
    }
    
    # Log de la transaction (sans données sensibles)
    app.logger.info(f'Redirection paiement - Commande: {order.order_number}, Montant: {order.total_amount} FCFA')
    
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
    # Récupération des paramètres (plusieurs formats possibles selon PayGate)
    order_number = request.args.get('identifier') or request.args.get('order_number')
    transaction_id = request.args.get('transaction_id') or request.args.get('tx_reference')
    status = request.args.get('status') or request.args.get('payment_status')
    
    # Log sécurisé pour audit (sans données sensibles)
    app.logger.info(f"Retour paiement - Commande: {order_number}, Status: {status}, TxID: {transaction_id}")
    
    # Validation : numéro de commande requis
    if not order_number:
        app.logger.warning('Retour paiement sans identifier')
        flash('Informations de paiement incomplètes. Vérifiez votre email pour la confirmation.', 'warning')
        return redirect(url_for('contact'))
    
    # Recherche de la commande
    order = Order.query.filter_by(order_number=order_number).first()
    
    if not order:
        app.logger.error(f'Commande introuvable: {order_number}')
        flash('Commande introuvable. Si vous avez effectué un paiement, contactez-nous avec votre numéro de commande.', 'error')
        return redirect(url_for('contact'))
    
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
                app.logger.error(f"Erreur envoi email pour commande {order_number}: {str(e)}")
        
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
        # Statut inconnu
        app.logger.warning(f"Statut de paiement inconnu pour commande {order_number}: {status}")
        flash('Paiement en cours de vérification. Consultez votre email pour la confirmation.', 'info')
        return redirect(url_for('confirmation', order_number=order.order_number))

@app.route('/payment/webhook', methods=['POST'])
def payment_webhook():
    """
    Webhook PayGate pour notifications de paiement
    Sécurisé avec vérification du secret webhook
    """
    # Vérification du secret webhook
    webhook_secret = request.headers.get('X-Webhook-Secret') or request.headers.get('X-PayGate-Signature')
    
    if not webhook_secret:
        app.logger.warning('Webhook reçu sans secret')
        return jsonify({'error': 'Unauthorized'}), 401
    
    if webhook_secret != app.config.get('PAYGATE_WEBHOOK_SECRET'):
        app.logger.warning(f'Webhook avec secret invalide: {webhook_secret[:10]}...')
        return jsonify({'error': 'Invalid webhook secret'}), 403
    
    # Récupération des données
    data = request.json or request.form.to_dict()
    
    order_number = data.get('identifier')
    transaction_id = data.get('transaction_id')
    status = data.get('status')
    amount = data.get('amount')
    
    # Log de la notification webhook
    app.logger.info(f'Webhook reçu - Commande: {order_number}, Status: {status}, TxID: {transaction_id}')
    
    if not order_number:
        app.logger.error('Webhook sans identifier')
        return jsonify({'error': 'Missing identifier'}), 400
    
    # Recherche de la commande
    order = Order.query.filter_by(order_number=order_number).first()
    
    if not order:
        app.logger.error(f'Webhook pour commande introuvable: {order_number}')
        return jsonify({'error': 'Order not found'}), 404
    
    # Vérification du montant (sécurité supplémentaire)
    if amount and int(amount) != int(order.total_amount):
        app.logger.error(f'Montant webhook ({amount}) != montant commande ({order.total_amount})')
        return jsonify({'error': 'Amount mismatch'}), 400
    
    # Mise à jour du statut selon la notification
    previous_status = order.payment_status
    
    if status in ['successful', 'completed', 'success']:
        order.payment_status = 'completed'
        order.payment_reference = transaction_id
        
        # Envoi de l'email de confirmation si pas déjà envoyé
        if previous_status != 'completed':
            try:
                qr_data = f"COLPRAD2025|{order.order_number}|{order.email}"
                qr_code = generate_qr_code(qr_data)
                send_confirmation_email(order, qr_code)
                app.logger.info(f'Email de confirmation envoyé pour {order_number}')
            except Exception as e:
                app.logger.error(f'Erreur envoi email webhook {order_number}: {str(e)}')
    
    elif status in ['failed', 'error', 'declined']:
        order.payment_status = 'failed'
    
    elif status in ['cancelled', 'canceled']:
        order.payment_status = 'cancelled'
    
    elif status in ['pending', 'processing']:
        order.payment_status = 'pending'
    
    db.session.commit()
    
    app.logger.info(f'Webhook traité - Commande {order_number}: {previous_status} → {order.payment_status}')
    
    return jsonify({
        'status': 'ok',
        'order_number': order_number,
        'payment_status': order.payment_status
    }), 200

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
    """
    Envoie l'email de confirmation avec le QR code au client
    """
    subject = f"✅ Confirmation COLPRAD 2025 - Billet {order.ticket_type.upper()} - Réf {order.order_number}"
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background: linear-gradient(135deg, #D8431A 0%, #0057A6 100%);
                color: white;
                padding: 30px;
                text-align: center;
                border-radius: 10px 10px 0 0;
            }}
            .content {{
                background: #ffffff;
                padding: 30px;
                border: 1px solid #e0e0e0;
            }}
            .qr-section {{
                background: #f8f9fa;
                padding: 30px;
                text-align: center;
                border: 3px dashed #D8431A;
                border-radius: 10px;
                margin: 20px 0;
            }}
            .qr-code {{
                max-width: 300px;
                width: 100%;
                height: auto;
                margin: 20px auto;
                display: block;
            }}
            .details {{
                background: #f8f9fa;
                padding: 20px;
                border-radius: 8px;
                margin: 20px 0;
            }}
            .details-row {{
                display: flex;
                justify-content: space-between;
                padding: 10px 0;
                border-bottom: 1px solid #e0e0e0;
            }}
            .details-row:last-child {{
                border-bottom: none;
            }}
            .label {{
                font-weight: bold;
                color: #0057A6;
            }}
            .value {{
                color: #333;
            }}
            .important {{
                background: #fff3cd;
                border-left: 4px solid #ffc107;
                padding: 15px;
                margin: 20px 0;
            }}
            .footer {{
                background: #f8f9fa;
                padding: 20px;
                text-align: center;
                border-radius: 0 0 10px 10px;
                font-size: 14px;
                color: #666;
            }}
            .btn {{
                display: inline-block;
                background: #D8431A;
                color: white;
                padding: 12px 30px;
                text-decoration: none;
                border-radius: 5px;
                margin: 10px 0;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🎉 Réservation Confirmée !</h1>
            <p>COLPRAD 2025 - Colloque des Professionnels de l'Art</p>
        </div>
        
        <div class="content">
            <h2>Bonjour {order.first_name} {order.last_name},</h2>
            
            <p>Merci pour votre réservation ! Nous sommes ravis de vous compter parmi les participants du COLPRAD 2025.</p>
            
            <div class="details">
                <h3 style="margin-top: 0; color: #D8431A;">📋 Détails de votre réservation</h3>
                <div class="details-row">
                    <span class="label">Numéro de commande :</span>
                    <span class="value"><strong>{order.order_number}</strong></span>
                </div>
                <div class="details-row">
                    <span class="label">Type de billet :</span>
                    <span class="value">{order.ticket_type.upper()}</span>
                </div>
                <div class="details-row">
                    <span class="label">Quantité :</span>
                    <span class="value">{order.quantity}</span>
                </div>
                <div class="details-row">
                    <span class="label">Montant payé :</span>
                    <span class="value"><strong>{order.total_amount:,.0f} FCFA</strong></span>
                </div>
                <div class="details-row">
                    <span class="label">Date de l'événement :</span>
                    <span class="value">13 Décembre 2025</span>
                </div>
                <div class="details-row">
                    <span class="label">Horaires :</span>
                    <span class="value">14H00 - 17H00</span>
                </div>
                <div class="details-row">
                    <span class="label">Lieu :</span>
                    <span class="value">Hôtel Elie Palace, Adidogomé - Lomé</span>
                </div>
            </div>
            
            <div class="qr-section">
                <h3 style="color: #D8431A; margin-top: 0;">📱 Votre QR Code d'Accès</h3>
                <p><strong>IMPORTANT : Présentez ce QR code à l'entrée le jour de l'événement</strong></p>
                <img src="{qr_code}" alt="QR Code" class="qr-code" />
                <p style="font-size: 18px; font-weight: bold; color: #0057A6;">{order.order_number}</p>
                <p style="font-size: 14px; color: #666;">Vous pouvez également présenter ce numéro de commande</p>
            </div>
            
            <div class="important">
                <strong>⚠️ À ne pas oublier le jour J :</strong>
                <ul style="margin: 10px 0;">
                    <li>Présentez votre QR code (imprimé ou sur smartphone)</li>
                    <li>Arrivez 30 minutes avant le début (dès 13H30)</li>
                    <li>Munissez-vous d'une pièce d'identité</li>
                    <li>Tenue professionnelle recommandée</li>
                </ul>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <p><strong>Besoin d'aide ?</strong></p>
                <p>
                    📧 Email : <a href="mailto:colpradofficiel@gmail.com">colpradofficiel@gmail.com</a><br>
                    📱 Téléphone : <a href="tel:+22892384092">+228 92 38 40 92</a><br>
                    💬 WhatsApp : <a href="https://wa.me/22892384092">+228 92 38 40 92</a>
                </p>
            </div>
        </div>
        
        <div class="footer">
            <p><strong>COLPRAD 2025</strong><br>
            Colloque des Professionnels de l'Art pour le Développement</p>
            <p>13 Décembre 2025 | 14H00-17H00 | Hôtel Elie Palace, Lomé</p>
            <p style="font-size: 12px; color: #999; margin-top: 20px;">
                Cet email a été envoyé à {order.email}<br>
                Si vous n'êtes pas à l'origine de cette réservation, veuillez nous contacter immédiatement.
            </p>
        </div>
    </body>
    </html>
    """
    
    try:
        msg = Message(subject, recipients=[order.email], html=html_body)
        mail.send(msg)
        app.logger.info(f'Email de confirmation envoyé à {order.email} pour commande {order.order_number}')
        return True
    except Exception as e:
        app.logger.error(f'Erreur envoi email {order.order_number}: {str(e)}')
        return False

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

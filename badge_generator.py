from reportlab.lib.pagesizes import mm
from reportlab.lib.units import mm as mm_unit
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.utils import ImageReader
from io import BytesIO
import qrcode

# Badge dimensions: 90mm x 135mm
BADGE_WIDTH = 90 * mm_unit
BADGE_HEIGHT = 135 * mm_unit
BLEED = 3 * mm_unit  # 3mm bleed

# Color codes
BADGE_COLORS = {
    'vip': '#D4AF37',
    'premium': '#9E9E9E',
    'standard': '#FFFFFF',
    'staff': '#0057A6',
    'hotesse': '#FF7F11',
    'presse': '#8B0000'
}

def generate_qr_code_image(data):
    """Generate QR code as PIL Image"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=2,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    return img

def draw_badge_front(c, order, y_offset=0):
    """Draw the front side of the badge"""
    x_start = BLEED
    y_start = y_offset + BLEED
    
    # Determine badge category and color
    category = order.ticket_type.lower()
    if category not in BADGE_COLORS:
        category = 'standard'
    
    color_hex = BADGE_COLORS[category]
    badge_color = HexColor(color_hex)
    
    # Background
    if category == 'standard':
        c.setFillColor(white)
        c.rect(x_start, y_start, BADGE_WIDTH, BADGE_HEIGHT, fill=1, stroke=1)
        c.setStrokeColor(black)
        c.setLineWidth(1)
        c.rect(x_start, y_start, BADGE_WIDTH, BADGE_HEIGHT, fill=0, stroke=1)
    else:
        c.setFillColor(white)
        c.rect(x_start, y_start, BADGE_WIDTH, BADGE_HEIGHT, fill=1, stroke=0)
    
    # Colored band at top (18% of height)
    band_height = BADGE_HEIGHT * 0.18
    c.setFillColor(badge_color)
    c.rect(x_start, y_start + BADGE_HEIGHT - band_height, BADGE_WIDTH, band_height, fill=1, stroke=0)
    
    # Logo area (placeholder)
    c.setFillColor(white if category != 'standard' else black)
    c.setFont("Helvetica-Bold", 20)
    logo_y = y_start + BADGE_HEIGHT - band_height/2 - 10
    c.drawCentredString(x_start + BADGE_WIDTH/2, logo_y, "COLPRAD 2025")
    
    # Category label
    c.setFillColor(white if category != 'standard' else black)
    c.setFont("Helvetica-Bold", 16)
    category_y = y_start + BADGE_HEIGHT - band_height - 15
    c.drawCentredString(x_start + BADGE_WIDTH/2, category_y, category.upper())
    
    # Participant name
    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 22)
    name_y = category_y - 25
    full_name = f"{order.first_name} {order.last_name}"
    c.drawCentredString(x_start + BADGE_WIDTH/2, name_y, full_name)
    
    # Organization
    if order.organization:
        c.setFont("Helvetica", 12)
        org_y = name_y - 18
        c.drawCentredString(x_start + BADGE_WIDTH/2, org_y, order.organization)
        info_y = org_y - 25
    else:
        info_y = name_y - 25
    
    # Ticket number and reference
    c.setFont("Helvetica", 10)
    c.drawCentredString(x_start + BADGE_WIDTH/2, info_y, 
                       f"Billet N° : {order.id:04d} — Réf : {order.order_number}")
    
    # QR Code (bottom left)
    qr_data = f"COLPRAD2025|{order.order_number}|{order.email}"
    qr_img = generate_qr_code_image(qr_data)
    
    # Convert PIL image to ReportLab ImageReader
    qr_buffer = BytesIO()
    qr_img.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)
    qr_reader = ImageReader(qr_buffer)
    
    qr_size = 35 * mm_unit
    qr_x = x_start + 5 * mm_unit
    qr_y = y_start + 5 * mm_unit
    c.drawImage(qr_reader, qr_x, qr_y, width=qr_size, height=qr_size)
    
    # Status icons (bottom right) - placeholder
    icon_x = x_start + BADGE_WIDTH - 25 * mm_unit
    icon_y = y_start + 10 * mm_unit
    c.setFont("Helvetica", 8)
    
    if category == 'vip':
        c.drawString(icon_x, icon_y, "★ VIP ACCESS")
    elif category == 'premium':
        c.drawString(icon_x, icon_y, "◆ PREMIUM")
    elif category == 'presse':
        c.drawString(icon_x, icon_y, "📷 PRESSE")
    elif category == 'staff':
        c.drawString(icon_x, icon_y, "👤 STAFF")

def draw_badge_back(c, y_offset=0):
    """Draw the back side of the badge"""
    x_start = BLEED
    y_start = y_offset + BLEED
    
    # Background
    c.setFillColor(white)
    c.rect(x_start, y_start, BADGE_WIDTH, BADGE_HEIGHT, fill=1, stroke=1)
    
    # Title
    c.setFillColor(HexColor('#0057A6'))
    c.setFont("Helvetica-Bold", 14)
    title_y = y_start + BADGE_HEIGHT - 20 * mm_unit
    c.drawCentredString(x_start + BADGE_WIDTH/2, title_y, "COLPRAD 2025")
    
    # Program summary
    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 10)
    prog_y = title_y - 15 * mm_unit
    c.drawString(x_start + 10 * mm_unit, prog_y, "Programme :")
    
    c.setFont("Helvetica", 9)
    prog_y -= 12
    c.drawString(x_start + 10 * mm_unit, prog_y, "Jour 1 : 09h00 - 18h00 | Politiques Culturelles")
    prog_y -= 10
    c.drawString(x_start + 10 * mm_unit, prog_y, "Jour 2 : 09h00 - 18h00 | Financement & Développement")
    prog_y -= 10
    c.drawString(x_start + 10 * mm_unit, prog_y, "Lieu : Lomé, Togo")
    
    # Emergency contacts
    c.setFont("Helvetica-Bold", 10)
    contact_y = prog_y - 20 * mm_unit
    c.drawString(x_start + 10 * mm_unit, contact_y, "Contacts d'urgence :")
    
    c.setFont("Helvetica", 9)
    contact_y -= 12
    c.drawString(x_start + 10 * mm_unit, contact_y, "Organisation : +228 XX XX XX XX")
    contact_y -= 10
    c.drawString(x_start + 10 * mm_unit, contact_y, "Email : contact@colprad.tg")
    
    # Terms and conditions
    c.setFont("Helvetica-Bold", 9)
    terms_y = contact_y - 20 * mm_unit
    c.drawString(x_start + 10 * mm_unit, terms_y, "Conditions d'accès :")
    
    c.setFont("Helvetica", 7)
    terms_y -= 10
    c.drawString(x_start + 10 * mm_unit, terms_y, "• Badge obligatoire pendant tout l'événement")
    terms_y -= 8
    c.drawString(x_start + 10 * mm_unit, terms_y, "• Billet non remboursable et non transférable")
    terms_y -= 8
    c.drawString(x_start + 10 * mm_unit, terms_y, "• Respecter les consignes de sécurité")
    terms_y -= 8
    c.drawString(x_start + 10 * mm_unit, terms_y, "• Présentation d'une pièce d'identité peut être requise")
    
    # Footer
    c.setFont("Helvetica-Oblique", 7)
    footer_y = y_start + 5 * mm_unit
    c.drawCentredString(x_start + BADGE_WIDTH/2, footer_y, 
                       "© 2025 Life Field Inc. - COLPRAD")

def generate_badge_pdf(order):
    """Generate a complete badge PDF (front and back) for an order"""
    buffer = BytesIO()
    
    # Create PDF with bleed
    page_width = BADGE_WIDTH + 2 * BLEED
    page_height = BADGE_HEIGHT + 2 * BLEED
    
    c = canvas.Canvas(buffer, pagesize=(page_width, page_height))
    
    # Page 1: Front
    draw_badge_front(c, order)
    c.showPage()
    
    # Page 2: Back
    draw_badge_back(c)
    c.showPage()
    
    c.save()
    buffer.seek(0)
    return buffer

def generate_multiple_badges_pdf(orders):
    """Generate badges for multiple orders in a single PDF"""
    buffer = BytesIO()
    
    page_width = BADGE_WIDTH + 2 * BLEED
    page_height = BADGE_HEIGHT + 2 * BLEED
    
    c = canvas.Canvas(buffer, pagesize=(page_width, page_height))
    
    for order in orders:
        # Front
        draw_badge_front(c, order)
        c.showPage()
        
        # Back
        draw_badge_back(c)
        c.showPage()
    
    c.save()
    buffer.seek(0)
    return buffer

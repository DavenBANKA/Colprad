from flask import Blueprint, render_template, request, redirect, url_for, flash
from uuid import uuid4

main_bp = Blueprint("main", __name__)

# In-memory catalog for initial scaffold
TICKETS = [
    {"code": "standard", "name": "Standard", "price": 5000},
    {"code": "premium", "name": "Premium", "price": 10000},
    {"code": "vip", "name": "VIP", "price": 20000},
    {"code": "invite", "name": "Gratuit (invitation)", "price": 0},
]


@main_bp.route("/")
def index():
    return render_template("index.html")


@main_bp.route("/a-propos")
def a_propos():
    return render_template("a_propos.html")


@main_bp.route("/programme")
def programme():
    return redirect(url_for("main.index"))



@main_bp.route("/intervenants")
def intervenants():
    return render_template("intervenants.html")


@main_bp.route("/infos-pratiques")
def infos_pratiques():
    return render_template("infos_pratiques.html")


@main_bp.route("/presse-partenaires")
def presse():
    return render_template("presse.html")


@main_bp.route("/contact")
def contact():
    return render_template("contact.html")


@main_bp.route("/billetterie")
def billetterie():
    return render_template("billetterie.html", tickets=TICKETS)


@main_bp.route("/reservation", methods=["GET", "POST"])
def reservation():
    if request.method == "POST":
        ticket_code = request.form.get("ticket_code")
        qty = int(request.form.get("quantity", 1))
        prenom = request.form.get("first_name")
        nom = request.form.get("last_name")
        email = request.form.get("email")
        phone = request.form.get("phone")

        ticket = next((t for t in TICKETS if t["code"] == ticket_code), None)
        if not ticket:
            flash("Type de billet invalide.", "danger")
            return redirect(url_for("main.billetterie"))

        total = ticket["price"] * qty
        order_ref = str(uuid4()).split("-")[0].upper()

        return redirect(
            url_for(
                "main.confirmation",
                ref=order_ref,
                type=ticket["name"],
                q=qty,
                total=total,
            )
        )

    # GET
    code = request.args.get("ticket")
    selected = next((t for t in TICKETS if t["code"] == code), None)
    return render_template("reservation.html", selected=selected, tickets=TICKETS)


@main_bp.route("/confirmation")
def confirmation():
    ref = request.args.get("ref")
    ticket_type = request.args.get("type")
    quantity = request.args.get("q")
    total = request.args.get("total")
    return render_template(
        "confirmation.html",
        ref=ref,
        ticket_type=ticket_type,
        quantity=quantity,
        total=total,
    )

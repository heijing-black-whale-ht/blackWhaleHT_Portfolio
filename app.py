from flask import Flask, render_template, request, flash, redirect, url_for, session, Response
from utils.icons import icon
import os
import requests
from dotenv import load_dotenv
from translations import translations

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


app = Flask(__name__)
app.jinja_env.globals["icon"] = icon
app.secret_key = os.getenv('SECRET_KEY')


@app.context_processor
def inject_translations():
    requested_language = request.args.get('lang')
    if requested_language in translations:
        session['lang'] = requested_language

    current_language = session.get('lang', 'en')
    return {
        't': translations[current_language],
        'current_language': current_language,
        'available_languages': translations,
    }


# Resend API Configuration
RESEND_API_KEY = os.getenv('RESEND_API_KEY')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/robots.txt')
def robots():
    robots_content = (
        'User-agent: *\n'
        'Allow: /\n'
        'Sitemap: https://www.heijinght.com/sitemap.xml\n'
    )
    return Response(robots_content, mimetype='text/plain')


@app.route('/sitemap.xml')
def sitemap():
    sitemap_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://www.heijinght.com/</loc>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>'''
    return Response(sitemap_xml, mimetype='application/xml')


@app.route("/language/<lang>")
def language(lang):
    available = ["en", "fr", "ht"]
    if lang in available:
        session["lang"] = lang
    return redirect(request.referrer or "/")

@app.route("/contact", methods=["POST"])
def contact():
    language = translations.get(session.get('lang', 'en'), translations['en'])

    if request.method == "POST":
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')

        if not name or not email or not subject or not message:
            flash(language['contact']['required_fields'], "danger")
            return redirect(url_for('home') + "#contact")

        if not RESEND_API_KEY:
            print("ERROR: RESEND_API_KEY environment variable is missing!")
            flash("Mail service configuration error. Please try again later.", "danger")
            return redirect(url_for('home') + "#contact")

        # Logo URL for embedding
        logo_url = url_for('static', filename='icons/outline/whale-logo.svg', _external=True)

        # Render the HTML templates
        admin_html_content = render_template(
            'admin_msg.html',
            name=name,
            email=email,
            subject=subject,
            message=message,
            logo_url=logo_url,
        )

        customer_html_content = render_template(
            'customer_msg.html',
            name=name,
            logo_url=logo_url,
        )

        
        # Send email using Resend API
        headers = {
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json"
        }

        admin_sent = False

        # 1. Send the notification email to ME (the Admin)
        try:
            admin_payload = {
                "from": "HEIJING HT Form <onboarding@resend.dev>",
                "to": [ADMIN_EMAIL],
                "reply_to": email,
                "subject": "New Contact Form Submission",
                "html": admin_html_content
            }

            admin_response = requests.post(
                "https://api.resend.com/emails",
                headers=headers,
                json=admin_payload,
                timeout=10
            )

            if admin_response.status_code in [200, 201]:
                admin_sent = True
                print("Admin notification email sent successfully via Resend API.")
            else:
                print(f"Resend API Admin Mail Error: {admin_response.status_code} - {admin_response.text}")

        except requests.exceptions.RequestException as e:
            print(f"Network exception while notifying Admin: {e}")

        # 2. Send the confirmation email to the Customer
        # NOTE: If the Resend account is in Sandbox mode, sending to unverified external emails 
        # will return an error. The try/except here ensures that a sandbox limit won't crash your site.
        if admin_sent:
            try:
                customer_payload = {
                    "from": "HEIJING HT <onboarding@resend.dev>",
                    "to": [ADMIN_EMAIL],  # In Sandbox, you can only send to verified emails; replace with sender_email in production
                    "subject": "Thank you for your message -- HEIJING HT",
                    "html": customer_html_content
                }
                
                customer_response = requests.post(
                    "https://api.resend.com/emails",
                    headers=headers,
                    json=customer_payload,
                    timeout=10
                )
                
                if customer_response.status_code in [200, 201]:
                    print("Customer confirmation email sent successfully via Resend API.")
                else:
                    print(f"Resend API Customer Mail Info (Expected restriction in unverified Sandbox): {customer_response.status_code} - {customer_response.text}")
            
            except requests.exceptions.RequestException as e:
                print(f"Network exception while emailing customer: {e}")

        # Flash alerts matched to whether you received the notification details
        if admin_sent:
            flash(language['contact']['success'], "success")
        else:
            flash(language['contact']['error'], "danger")

        return redirect(url_for('home') + "#contact")
    return redirect(url_for('home') + "#contact")


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
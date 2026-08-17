import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app

def send_email(subject, recipient, html_content, text_content=None):
    """
    Sends email via SMTP or logs to stdout if SMTP is unconfigured.
    """
    server_host = current_app.config.get('MAIL_SERVER')
    server_port = current_app.config.get('MAIL_PORT', 587)
    username = current_app.config.get('MAIL_USERNAME')
    password = current_app.config.get('MAIL_PASSWORD')
    sender = current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@exportweb.com')

    if not username or not password:
        print(f"\n================ [EMAIL NOTIFICATION MOCK] ================")
        print(f"TO: {recipient}")
        print(f"FROM: {sender}")
        print(f"SUBJECT: {subject}")
        print(f"BODY:\n{text_content or html_content}")
        print(f"===========================================================\n")
        return True

    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = recipient

        if text_content:
            msg.attach(MIMEText(text_content, 'plain'))
        if html_content:
            msg.attach(MIMEText(html_content, 'html'))

        with smtplib.SMTP(server_host, server_port) as server:
            if current_app.config.get('MAIL_USE_TLS', True):
                server.starttls()
            server.login(username, password)
            server.sendmail(sender, [recipient], msg.as_string())
        return True
    except Exception as e:
        print(f"[SMTP Error] Failed to send email to {recipient}: {e}")
        return False


def send_enquiry_notification(enquiry, seller):
    subject = f"New Lead: Inquiry from {enquiry.buyer_name} ({enquiry.company or 'Buyer'})"
    
    html_content = f"""
    <h2>New Export Inquiry Received</h2>
    <p>Dear {seller.company_name},</p>
    <p>You have received a new business enquiry on <strong>GlobalExportHub</strong>.</p>
    <table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 100%;">
        <tr><td><strong>Buyer Name:</strong></td><td>{enquiry.buyer_name}</td></tr>
        <tr><td><strong>Company:</strong></td><td>{enquiry.company or 'N/A'}</td></tr>
        <tr><td><strong>Email:</strong></td><td>{enquiry.email}</td></tr>
        <tr><td><strong>Phone:</strong></td><td>{enquiry.phone or 'N/A'}</td></tr>
        <tr><td><strong>Country:</strong></td><td>{enquiry.country or 'N/A'}</td></tr>
        <tr><td><strong>Requested Quantity:</strong></td><td>{enquiry.quantity or 'N/A'}</td></tr>
        <tr><td><strong>Message:</strong></td><td>{enquiry.message}</td></tr>
    </table>
    <p>Log in to your seller dashboard to manage and reply to this lead.</p>
    """
    
    seller_email = seller.user.email if seller.user else None
    if seller_email:
        send_email(subject, seller_email, html_content)


def send_approval_status_email(seller, status, reason=None):
    subject = f"Seller Account Status Update: {status.upper()}"
    
    if status == 'approved':
        html_content = f"""
        <h2>Congratulations! Your Exporter Portfolio is Approved</h2>
        <p>Dear {seller.company_name},</p>
        <p>Your company profile and export documentation have been reviewed and approved by our team.</p>
        <p>Your dynamic portfolio is now live at: <strong>/sellers/{seller.slug}</strong></p>
        <p>Global buyers can now view your products, certifications, and send direct enquiries.</p>
        """
    else:
        html_content = f"""
        <h2>Seller Account Status Update</h2>
        <p>Dear {seller.company_name},</p>
        <p>Your seller registration status has been updated to: <strong>{status.upper()}</strong>.</p>
        {'<p><strong>Reason/Feedback:</strong> ' + reason + '</p>' if reason else ''}
        <p>Please log in to your dashboard to update required details and resubmit.</p>
        """
        
    seller_email = seller.user.email if seller.user else None
    if seller_email:
        send_email(subject, seller_email, html_content)

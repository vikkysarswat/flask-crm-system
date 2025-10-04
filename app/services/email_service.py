"""Email service for sending emails.

Yeh module email sending functionality provide karta hai.
SendGrid integration ke saath.

"""

from flask import current_app
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
import logging


logger = logging.getLogger(__name__)


def send_email(to_email, subject, content, from_email=None):
    """Send email using SendGrid.
    
    Email send karta hai SendGrid API ke through.
    
    Args:
        to_email (str): Recipient email address
        subject (str): Email subject
        content (str): Email content (HTML or plain text)
        from_email (str): Sender email (optional)
        
    Returns:
        bool: True if sent successfully, False otherwise
        
    Example:
        >>> success = send_email(
        ...     'customer@example.com',
        ...     'Welcome to CRM',
        ...     '<h1>Welcome!</h1>'
        ... )
    """
    try:
        # Get API key from config
        api_key = current_app.config.get('MAIL_API_KEY')
        
        if not api_key:
            logger.warning('SendGrid API key not configured')
            return False
        
        # Set sender email
        if not from_email:
            from_email = current_app.config.get('MAIL_DEFAULT_SENDER')
        
        # Create message
        message = Mail(
            from_email=Email(from_email),
            to_emails=To(to_email),
            subject=subject,
            html_content=Content('text/html', content)
        )
        
        # Send email
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        
        if response.status_code in [200, 201, 202]:
            logger.info(f'Email sent successfully to {to_email}')
            return True
        else:
            logger.error(f'Failed to send email: {response.status_code}')
            return False
            
    except Exception as e:
        logger.error(f'Error sending email: {str(e)}')
        return False


def send_bulk_email(recipients, subject, content, from_email=None):
    """Send bulk emails to multiple recipients.
    
    Multiple recipients ko email send karta hai.
    
    Args:
        recipients (list): List of email addresses
        subject (str): Email subject
        content (str): Email content
        from_email (str): Sender email (optional)
        
    Returns:
        dict: Results with success and failure counts
    """
    success_count = 0
    failure_count = 0
    
    for recipient in recipients:
        if send_email(recipient, subject, content, from_email):
            success_count += 1
        else:
            failure_count += 1
    
    return {
        'success': success_count,
        'failed': failure_count,
        'total': len(recipients)
    }

"""SMS service for sending text messages.

Yeh module SMS sending functionality provide karta hai.
Twilio integration ke saath.

"""

from flask import current_app
from twilio.rest import Client
import logging


logger = logging.getLogger(__name__)


def send_sms(to_phone, message, from_phone=None):
    """Send SMS using Twilio.
    
    SMS send karta hai Twilio API ke through.
    
    Args:
        to_phone (str): Recipient phone number (with country code)
        message (str): SMS message text
        from_phone (str): Sender phone number (optional)
        
    Returns:
        bool: True if sent successfully, False otherwise
        
    Example:
        >>> success = send_sms(
        ...     '+919876543210',
        ...     'Your appointment is confirmed'
        ... )
    """
    try:
        # Get Twilio credentials
        account_sid = current_app.config.get('TWILIO_ACCOUNT_SID')
        auth_token = current_app.config.get('TWILIO_AUTH_TOKEN')
        
        if not account_sid or not auth_token:
            logger.warning('Twilio credentials not configured')
            return False
        
        # Set sender phone
        if not from_phone:
            from_phone = current_app.config.get('TWILIO_PHONE_NUMBER')
        
        if not from_phone:
            logger.error('Twilio phone number not configured')
            return False
        
        # Create Twilio client
        client = Client(account_sid, auth_token)
        
        # Send SMS
        message = client.messages.create(
            body=message,
            from_=from_phone,
            to=to_phone
        )
        
        if message.sid:
            logger.info(f'SMS sent successfully to {to_phone}')
            return True
        else:
            logger.error('Failed to send SMS')
            return False
            
    except Exception as e:
        logger.error(f'Error sending SMS: {str(e)}')
        return False


def send_bulk_sms(recipients, message, from_phone=None):
    """Send bulk SMS to multiple recipients.
    
    Multiple recipients ko SMS send karta hai.
    
    Args:
        recipients (list): List of phone numbers
        message (str): SMS message text
        from_phone (str): Sender phone number (optional)
        
    Returns:
        dict: Results with success and failure counts
    """
    success_count = 0
    failure_count = 0
    
    for recipient in recipients:
        if send_sms(recipient, message, from_phone):
            success_count += 1
        else:
            failure_count += 1
    
    return {
        'success': success_count,
        'failed': failure_count,
        'total': len(recipients)
    }

"""Notification service for push notifications.

Yeh module push notifications send karta hai.
Firebase Cloud Messaging integration ke saath.

"""

from flask import current_app
from pyfcm import FCMNotification
import logging


logger = logging.getLogger(__name__)


def send_push_notification(device_token, title, message, data=None):
    """Send push notification using Firebase Cloud Messaging.
    
    Push notification send karta hai FCM ke through.
    
    Args:
        device_token (str): Device FCM token
        title (str): Notification title
        message (str): Notification message
        data (dict): Additional data payload (optional)
        
    Returns:
        bool: True if sent successfully, False otherwise
        
    Example:
        >>> success = send_push_notification(
        ...     'device_token_here',
        ...     'New Lead',
        ...     'You have a new hot lead!'
        ... )
    """
    try:
        # Get FCM server key
        server_key = current_app.config.get('FCM_SERVER_KEY')
        
        if not server_key:
            logger.warning('FCM server key not configured')
            return False
        
        # Create FCM client
        push_service = FCMNotification(api_key=server_key)
        
        # Send notification
        result = push_service.notify_single_device(
            registration_id=device_token,
            message_title=title,
            message_body=message,
            data_message=data
        )
        
        if result.get('success'):
            logger.info(f'Push notification sent successfully')
            return True
        else:
            logger.error(f'Failed to send push notification')
            return False
            
    except Exception as e:
        logger.error(f'Error sending push notification: {str(e)}')
        return False


def send_bulk_push_notification(device_tokens, title, message, data=None):
    """Send push notification to multiple devices.
    
    Multiple devices ko notification send karta hai.
    
    Args:
        device_tokens (list): List of device FCM tokens
        title (str): Notification title
        message (str): Notification message
        data (dict): Additional data payload (optional)
        
    Returns:
        dict: Results with success and failure counts
    """
    try:
        server_key = current_app.config.get('FCM_SERVER_KEY')
        
        if not server_key:
            logger.warning('FCM server key not configured')
            return {'success': 0, 'failed': len(device_tokens)}
        
        push_service = FCMNotification(api_key=server_key)
        
        result = push_service.notify_multiple_devices(
            registration_ids=device_tokens,
            message_title=title,
            message_body=message,
            data_message=data
        )
        
        return {
            'success': result.get('success', 0),
            'failed': result.get('failure', 0),
            'total': len(device_tokens)
        }
        
    except Exception as e:
        logger.error(f'Error sending bulk push notifications: {str(e)}')
        return {
            'success': 0,
            'failed': len(device_tokens),
            'total': len(device_tokens)
        }

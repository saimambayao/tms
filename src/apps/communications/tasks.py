from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import CommunicationMessage, CommunicationCampaign
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)

@shared_task
def send_single_message(message_id):
    """
    Sends a single CommunicationMessage.
    """
    try:
        message = CommunicationMessage.objects.get(id=message_id)
        
        # Ensure recipient has an email
        if not message.recipient.email:
            message.status = 'failed'
            message.error_message = "Recipient has no email address."
            message.save()
            logger.warning(f"Message {message_id} failed: Recipient has no email.")
            return
            
        # Send email
        send_mail(
            message.subject,
            message.content,
            settings.DEFAULT_FROM_EMAIL,
            [message.recipient.email],
            fail_silently=False,
        )
        
        message.status = 'sent'
        message.sent_at = timezone.now()
        message.save()
        logger.info(f"Message {message_id} sent successfully to {message.recipient.email}.")
        
    except CommunicationMessage.DoesNotExist:
        logger.error(f"CommunicationMessage with ID {message_id} not found.")
    except Exception as e:
        message = CommunicationMessage.objects.get(id=message_id) # Re-fetch in case of error before save
        message.status = 'failed'
        message.error_message = str(e)
        message.retry_count += 1
        message.save()
        logger.error(f"Error sending message {message_id}: {e}")


@shared_task
def send_campaign_messages(campaign_id):
    """
    Sends all messages for a given CommunicationCampaign.
    """
    try:
        campaign = CommunicationCampaign.objects.get(id=campaign_id)
        recipients = campaign.get_recipients()
        
        successful_sends = 0
        failed_sends = 0
        
        for recipient_user in recipients:
            # Create a CommunicationMessage for each recipient
            message = CommunicationMessage.objects.create(
                campaign=campaign,
                recipient=recipient_user,
                message_type=campaign.template.template_type if campaign.template else 'email', # Use template type or default
                subject=campaign.subject,
                content=campaign.content,
                # Add more fields if needed, e.g., IP address, user agent
            )
            
            # Call the single message sending task
            try:
                send_single_message.delay(message.id)
                successful_sends += 1
            except Exception as e:
                logger.error(f"Failed to queue message {message.id} for campaign {campaign_id}: {e}")
                failed_sends += 1
        
        campaign.successful_sends = successful_sends
        campaign.failed_sends = failed_sends
        campaign.status = 'sent'
        campaign.sent_time = timezone.now()
        campaign.save()
        logger.info(f"Campaign {campaign_id} completed. Successful: {successful_sends}, Failed: {failed_sends}")
        
    except CommunicationCampaign.DoesNotExist:
        logger.error(f"CommunicationCampaign with ID {campaign_id} not found.")
    except Exception as e:
        logger.error(f"Error in send_campaign_messages for campaign {campaign_id}: {e}")

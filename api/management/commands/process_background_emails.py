from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from api.models import AIWeekendRegistration, AIWeekendLead
from api.email_utils import send_ai_weekend_access_details, send_abandoned_cart_email
import time

class Command(BaseCommand):
    help = 'Process delayed emails for AI Weekend (abandoned cart & access details)'

    def handle(self, *args, **options):
        now = timezone.now()
        
        # 1. Access Details Emails (10 mins after payment)
        ten_mins_ago = now - timedelta(minutes=10)
        pending_access = AIWeekendRegistration.objects.filter(
            is_paid=True, 
            access_email_sent=False, 
            created_at__lte=ten_mins_ago
        )
        
        if pending_access.exists():
            self.stdout.write(f"Sending {pending_access.count()} access emails...")
            for reg in pending_access:
                try:
                    success = send_ai_weekend_access_details(reg.email)
                    if success:
                        reg.access_email_sent = True
                        reg.save()
                    time.sleep(1)
                except Exception as e:
                    self.stderr.write(f"Error sending access email to {reg.email}: {e}")

        # 2. Abandoned Cart Emails
        # Paid users should not receive abandoned cart emails
        paid_emails = set(AIWeekendRegistration.objects.filter(is_paid=True).values_list('email', flat=True))
        
        # Level 1 (10 mins)
        pending_lvl1 = AIWeekendLead.objects.filter(email_1_sent=False, created_at__lte=ten_mins_ago)
        if pending_lvl1.exists():
            self.stdout.write(f"Processing {pending_lvl1.count()} Level 1 abandoned cart emails...")
            for lead in pending_lvl1:
                if lead.email not in paid_emails:
                    try:
                        success = send_abandoned_cart_email(lead.email, lead.name, level=1)
                        if success:
                            lead.email_1_sent = True
                            lead.save()
                        time.sleep(1)
                    except Exception as e:
                        self.stderr.write(f"Error lvl 1 to {lead.email}: {e}")
                else:
                    lead.email_1_sent = True
                    lead.save()
                
        # Level 2 (20 mins)
        twenty_mins_ago = now - timedelta(minutes=20)
        pending_lvl2 = AIWeekendLead.objects.filter(email_2_sent=False, created_at__lte=twenty_mins_ago)
        if pending_lvl2.exists():
            self.stdout.write(f"Processing {pending_lvl2.count()} Level 2 abandoned cart emails...")
            for lead in pending_lvl2:
                if lead.email not in paid_emails:
                    if lead.email_1_sent:
                        try:
                            success = send_abandoned_cart_email(lead.email, lead.name, level=2)
                            if success:
                                lead.email_2_sent = True
                                lead.save()
                            time.sleep(1)
                        except Exception as e:
                            self.stderr.write(f"Error lvl 2 to {lead.email}: {e}")
                else:
                    lead.email_2_sent = True
                    lead.save()
                
        # Level 3 (30 mins)
        thirty_mins_ago = now - timedelta(minutes=30)
        pending_lvl3 = AIWeekendLead.objects.filter(email_3_sent=False, created_at__lte=thirty_mins_ago)
        if pending_lvl3.exists():
            self.stdout.write(f"Processing {pending_lvl3.count()} Level 3 abandoned cart emails...")
            for lead in pending_lvl3:
                if lead.email not in paid_emails:
                    if lead.email_2_sent: 
                        try:
                            success = send_abandoned_cart_email(lead.email, lead.name, level=3)
                            if success:
                                lead.email_3_sent = True
                                lead.save()
                            time.sleep(1)
                        except Exception as e:
                            self.stderr.write(f"Error lvl 3 to {lead.email}: {e}")
                else:
                    lead.email_3_sent = True
                    lead.save()
                    
        # 3. September 18th, 2026 @ 7:00 PM Meeting Link Blast
        from datetime import datetime
        import pytz
        
        # We will use naive datetime and make it aware in the current timezone, or better just use UTC timestamp if unsure, 
        # but let's assume local time Sept 18th 19:00. To avoid tz errors:
        target_time = timezone.make_aware(datetime(2026, 9, 18, 19, 0))
        
        if now >= target_time:
            pending_meeting_links = AIWeekendRegistration.objects.filter(
                is_paid=True, 
                meeting_link_sent=False
            )
            
            if pending_meeting_links.exists():
                from api.email_utils import send_ai_weekend_meeting_link
                self.stdout.write(f"Sending {pending_meeting_links.count()} Meeting Link emails for Sept 18th blast...")
                for reg in pending_meeting_links:
                    try:
                        success = send_ai_weekend_meeting_link(reg.email)
                        if success:
                            reg.meeting_link_sent = True
                            reg.save()
                        time.sleep(1)
                    except Exception as e:
                        self.stderr.write(f"Error sending meeting link to {reg.email}: {e}")
                    
        self.stdout.write(self.style.SUCCESS("Background email processing complete."))

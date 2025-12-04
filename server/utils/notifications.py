import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List, Dict, Any
from abc import ABC, abstractmethod
from datetime import datetime
from dataclasses import dataclass

from config.settings import settings


@dataclass
class PriceDropAlert:
    product_name: str
    current_price: float
    target_price: float
    product_url: str
    
    @property
    def savings(self) -> float:
        return self.target_price - self.current_price


@dataclass
class FakeDiscountAlert:
    product_name: str
    claimed_discount: float
    actual_discount: float
    reason: str
    product_url: str


class AlertMessageBuilder:
    def build_price_drop_text(self, alert: PriceDropAlert) -> str:
        return f"""Good news! The price has dropped to your target.

Product: {alert.product_name}
Current Price: ${alert.current_price:.2f}
Your Target: ${alert.target_price:.2f}
Savings: ${alert.savings:.2f}

View Product: {alert.product_url}

This is an automated alert from Retail Price Intelligence System."""

    def build_price_drop_html(self, alert: PriceDropAlert) -> str:
        return f"""<html>
<body style="font-family: Arial, sans-serif;">
    <h2 style="color: #2e7d32;">Price Alert: {alert.product_name}</h2>
    <p>Good news! The price has dropped to your target.</p>
    <table style="border-collapse: collapse; margin: 20px 0;">
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Product:</strong></td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{alert.product_name}</td>
        </tr>
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Current Price:</strong></td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd; color: #2e7d32; font-weight: bold;">${alert.current_price:.2f}</td>
        </tr>
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Your Target:</strong></td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">${alert.target_price:.2f}</td>
        </tr>
        <tr>
            <td style="padding: 8px;"><strong>Savings:</strong></td>
            <td style="padding: 8px; color: #2e7d32;">${alert.savings:.2f}</td>
        </tr>
    </table>
    <p><a href="{alert.product_url}" style="background-color: #1976d2; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px;">View Product</a></p>
    <p style="color: #666; font-size: 12px; margin-top: 30px;">This is an automated alert from Retail Price Intelligence System.</p>
</body>
</html>"""

    def build_fake_discount_text(self, alert: FakeDiscountAlert) -> str:
        return f"""Warning: A potential fake discount has been detected.

Product: {alert.product_name}
Claimed Discount: {alert.claimed_discount:.1f}%
Actual Discount: {alert.actual_discount:.1f}%
Reason: {alert.reason}

View Product: {alert.product_url}

This is an automated alert from Retail Price Intelligence System."""


class NotificationService(ABC):
    @abstractmethod
    def send(self, recipient: str, subject: str, message: str, **kwargs) -> bool:
        pass


class SMTPConfig:
    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        use_tls: bool = True,
        from_email: Optional[str] = None
    ):
        self.host = host or os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.port = port or int(os.getenv('SMTP_PORT', 587))
        self.user = user or os.getenv('SMTP_USER', '')
        self.password = password or os.getenv('SMTP_PASSWORD', '')
        self.use_tls = use_tls
        self.from_email = from_email or os.getenv('SMTP_FROM_EMAIL', self.user)
    
    @property
    def is_configured(self) -> bool:
        return bool(self.user and self.password)


class EmailNotificationService(NotificationService):
    def __init__(self, config: Optional[SMTPConfig] = None):
        self.config = config or SMTPConfig()
    
    def send(self, recipient: str, subject: str, message: str, html_message: Optional[str] = None) -> bool:
        if not self.config.is_configured:
            return False
        
        try:
            msg = self._build_message(recipient, subject, message, html_message)
            self._send_via_smtp(recipient, msg)
            return True
        except Exception:
            return False
    
    def _build_message(self, recipient: str, subject: str, message: str, html_message: Optional[str]) -> MIMEMultipart:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = self.config.from_email
        msg['To'] = recipient
        
        msg.attach(MIMEText(message, 'plain'))
        
        if html_message:
            msg.attach(MIMEText(html_message, 'html'))
        
        return msg
    
    def _send_via_smtp(self, recipient: str, msg: MIMEMultipart) -> None:
        with smtplib.SMTP(self.config.host, self.config.port) as server:
            if self.config.use_tls:
                server.starttls()
            server.login(self.config.user, self.config.password)
            server.sendmail(self.config.from_email, recipient, msg.as_string())
    
    def send_batch(self, recipients: List[str], subject: str, message: str, 
                   html_message: Optional[str] = None) -> Dict[str, bool]:
        return {recipient: self.send(recipient, subject, message, html_message) for recipient in recipients}


class WebhookNotificationService(NotificationService):
    SUCCESS_STATUS_CODES = (200, 201, 202, 204)
    
    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url or os.getenv('WEBHOOK_URL', '')
    
    def send(self, recipient: str, subject: str, message: str, **kwargs) -> bool:
        import requests
        
        url = recipient if recipient.startswith('http') else self.webhook_url
        if not url:
            return False
        
        try:
            payload = self._build_payload(subject, message, **kwargs)
            response = requests.post(url, json=payload, timeout=10)
            return response.status_code in self.SUCCESS_STATUS_CODES
        except Exception:
            return False
    
    def _build_payload(self, subject: str, message: str, **kwargs) -> Dict[str, Any]:
        return {
            'title': subject,
            'message': message,
            'timestamp': datetime.utcnow().isoformat(),
            **kwargs
        }


class SlackNotificationService(NotificationService):
    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url or os.getenv('SLACK_WEBHOOK_URL', '')
    
    def send(self, recipient: str, subject: str, message: str, **kwargs) -> bool:
        import requests
        
        if not self.webhook_url:
            return False
        
        try:
            payload = self._build_payload(recipient, subject, message)
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            return response.status_code == 200
        except Exception:
            return False
    
    def _build_payload(self, recipient: str, subject: str, message: str) -> Dict[str, Any]:
        payload = {'text': f"*{subject}*\n{message}"}
        if recipient.startswith('#'):
            payload['channel'] = recipient
        return payload


class PriceAlertNotifier:
    def __init__(
        self,
        email_service: Optional[NotificationService] = None,
        webhook_service: Optional[NotificationService] = None,
        slack_service: Optional[NotificationService] = None
    ):
        self.email_service = email_service or EmailNotificationService()
        self.webhook_service = webhook_service or WebhookNotificationService()
        self.slack_service = slack_service or SlackNotificationService()
        self._message_builder = AlertMessageBuilder()
    
    def notify_price_drop(
        self,
        product_name: str,
        current_price: float,
        target_price: float,
        product_url: str,
        email: Optional[str] = None,
        webhook_url: Optional[str] = None,
        slack_channel: Optional[str] = None
    ) -> Dict[str, bool]:
        alert = PriceDropAlert(product_name, current_price, target_price, product_url)
        subject = f"Price Alert: {product_name}"
        message = self._message_builder.build_price_drop_text(alert)
        html_message = self._message_builder.build_price_drop_html(alert)
        
        results = {}
        
        if email:
            results['email'] = self.email_service.send(email, subject, message, html_message=html_message)
        
        if webhook_url:
            results['webhook'] = self.webhook_service.send(
                webhook_url, subject, message,
                product_name=product_name,
                current_price=current_price,
                target_price=target_price,
                product_url=product_url
            )
        
        if slack_channel:
            results['slack'] = self.slack_service.send(slack_channel, subject, message)
        
        return results
    
    def notify_fake_discount(
        self,
        product_name: str,
        claimed_discount: float,
        actual_discount: float,
        reason: str,
        product_url: str,
        email: Optional[str] = None
    ) -> Dict[str, bool]:
        alert = FakeDiscountAlert(product_name, claimed_discount, actual_discount, reason, product_url)
        subject = f"Fake Discount Alert: {product_name}"
        message = self._message_builder.build_fake_discount_text(alert)
        
        results = {}
        
        if email:
            results['email'] = self.email_service.send(email, subject, message)
        
        return results


notifier = PriceAlertNotifier()

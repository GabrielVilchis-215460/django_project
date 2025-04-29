from django.test import TestCase
from django.core.mail import send_mail
from django.core import mail
# Create your tests here.

class EmailTest(TestCase):
    def test_send_email(self):
        send_mail(
            'Hola desde django!',
            'Este es un correo de prueba enviado desde Django usando Gmail',
            'g2vilchis@gmail.com',
            ['hermoxa77@gmail.com'],
            fail_silently=False,
        )
        self.assertEqual(len(mail.outbox),1)
        email = mail.outbox[0]
        self.assertEqual(email.subject, 'Hola desde django!')
        self.assertEqual(email.body, 'Este es un correo de prueba enviado desde Django usando Gmail')
        self.assertEqual(email.from_email, 'g2vilchis@gmail.com')
        self.assertEqual(email.to, ['hermoxa77@gmail.com'])
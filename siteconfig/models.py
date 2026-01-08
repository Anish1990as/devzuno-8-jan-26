from django.db import models

class SiteSettings(models.Model):
    company_name = models.CharField(max_length=120, default='Devzuno Technologies')
    whatsapp = models.CharField(max_length=20, default='+919219317352')
    support_email = models.EmailField(default='support@devzuno.com')
    razorpay_mode = models.CharField(max_length=10, choices=[('demo','Demo'),('live','Live')], default='demo')
    razorpay_key_id = models.CharField(max_length=200, blank=True, default='')
    razorpay_key_secret = models.CharField(max_length=200, blank=True, default='')

    logo_text = models.CharField(max_length=60, default='Devzuno')
    hero_title = models.CharField(max_length=200, default='Build, launch & manage your digital business')
    hero_subtitle = models.CharField(max_length=300, default='Websites, apps, domains, invoices, tickets — all in one platform.')

    class Meta:
        verbose_name = 'Site Setting'
        verbose_name_plural = 'Site Settings'

    def __str__(self):
        return 'Site Settings'

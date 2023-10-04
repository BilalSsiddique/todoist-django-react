from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import List
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

User = get_user_model()

@receiver(post_save,sender=User)
def send_welcome_email(sender,instance,created,**kwargs):
    if created:
        subject = 'Welcome to our platform!'
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = instance.email
        html_content = render_to_string('welcome_email.html', {'user': instance})
        text_content = "This is an important message."
        email_message = EmailMultiAlternatives(subject,text_content,from_email, [to_email])
        email_message.attach_alternative(html_content, "text/html")
        num_sent = email_message.send()
        if num_sent == 1:
            print('successful')
        else:
            print('fail')
       

@receiver(post_save, sender=User)
def create_initial_lists(sender, instance, created, **kwargs):
    if created:
        print('invokded &&&&')
        initial_lists = [
    "Personal Tasks",
    "Work Tasks",
    "Shopping List",
    "Home Tasks",
    "Groceries",
    "Books to Read",
    "Movies to Watch",
    "Fitness Goals",
    "Travel Plans",
    "Long-term Goals"
    ]  
        for title in initial_lists:
            List.objects.create(list_title=title, user_id=instance)

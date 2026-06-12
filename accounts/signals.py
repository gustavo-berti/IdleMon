from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import PerfilTreinador

User = get_user_model()


@receiver(post_save, sender=User)
def create_trainer_profile(sender, instance, created, **kwargs):
    """Cria automaticamente um PerfilTreinador quando um User é criado"""
    if created:
        PerfilTreinador.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_trainer_profile(sender, instance, **kwargs):
    """Salva o PerfilTreinador quando o User é salvo"""
    if hasattr(instance, 'trainer_profile'):
        instance.trainer_profile.save()

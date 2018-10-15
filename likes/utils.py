from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from .models import Like
from .settings import LIKES_MODELS

__all__ = (
    'allowed_content_type',
    'user_likes_count',
    'obj_likes_count',
    'is_liked',
    'get_who_liked',
    'admin_change_url'
)

User = get_user_model()


def allowed_content_type(ct) -> bool:
    name = f'{ct.app_label}.{ct.model.title()}'
    if name in LIKES_MODELS.keys():
        return True
    return False


def user_likes_count(user: User) -> int:
    """
    Returns count of likes for a given user.
    """
    if not user.is_authenticated:
        return 0
    return (
        Like.objects
        .filter(
            sender=user,
            content_type__isnull=False,
            object_id__isnull=False
        )
        .count()
    )


def obj_likes_count(obj) -> int:
    """
    Returns count of likes for a given object.
    """
    return (
        Like.objects
        .filter(
            content_type=ContentType.objects.get_for_model(obj),
            object_id=obj.pk
        )
        .count()
    )


def is_liked(obj, user: User) -> bool:
    """
    Checks if a given object is liked by a given user.
    """
    if not user.is_authenticated:
        return False
    ct = ContentType.objects.get_for_model(obj)
    return (
        Like.objects
        .filter(
            content_type=ct,
            object_id=obj.pk,
            sender=user
        )
        .exists()
    )


def get_who_liked(obj):
    """
    Returns users, who liked a given object.
    """
    ct = ContentType.objects.get_for_model(obj)
    return (
        User.objects
        .filter(
            likes__content_type=ct,
            likes__object_id=obj.pk
        )
    )


def admin_change_url(obj) -> str:
    """
    Returns admin change url for a given object.
    """
    app_label = obj._meta.app_label
    model_name = obj._meta.model.__name__.lower()
    return reverse(
        f'admin:{app_label}_{model_name}_change',
        args=(obj.pk,)
    )

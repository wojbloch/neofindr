from typing import Optional, TypeVar
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.db.models import Model


# TODO: IMPLEMENT CASCADE SOFT DEL + RESTORE

T = TypeVar('T', bound=Model)

class SoftDeleteBehavior:
    @staticmethod
    def soft_delete(instance: T, user: Optional['User'] = None) -> T:
        from core.models import SoftDeleteFact, User
        instance.is_deleted = True
        instance.deleted_at = timezone.now()
        instance.save()

        content_type = ContentType.objects.get_for_model(type(instance))
        SoftDeleteFact.objects.create(content_type=content_type, object_id=instance.pk, deleted_by=user)

        return instance

    @staticmethod
    def restore(instance: T, user: Optional['User'] = None) -> T:
        from core.models import SoftDeleteFact, User
        instance.is_deleted = False
        instance.deleted_at = None
        instance.save()

        content_type = ContentType.objects.get_for_model(type(instance))
        deletion_fact = SoftDeleteFact.objects.filter(content_type=content_type, object_id=instance.pk, restored_at=None).order_by('-deleted_at').first()

        if deletion_fact:
            deletion_fact.restored_at = timezone.now()
            deletion_fact.restored_by = user
            deletion_fact.save()

        return instance

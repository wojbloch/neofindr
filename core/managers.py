from django.db import models
from django.db.models import QuerySet
from django.utils import timezone


class SoftDeleteManager(models.Manager):
    def get_queryset(self) -> QuerySet:
        return super().get_queryset().filter(is_deleted=False)

    def delete(self) -> int:
        return self.update(is_deleted=True, deleted_at=timezone.now())


class SoftDeletedManager(SoftDeleteManager):
    def get_queryset(self) -> QuerySet:
        return super().get_queryset().filter(is_deleted=True)

    def restore(self) -> int:
        return self.update(is_deleted=False, deleted_at=None)

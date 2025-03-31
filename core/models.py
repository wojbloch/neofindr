from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import ForeignKey
from utils.constants import SENIORITY_LEVEL_CHOICES, WORK_MODE_CHOICES
from core.managers import SoftDeleteManager, SoftDeletedManager
from utils.model_behavior import SoftDeleteBehavior


class User(AbstractUser):
    pass

class SoftDeleteFact(models.Model):
    content_type = models.ForeignKey('contenttypes.ContentType', on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    deleted_at = models.DateTimeField(auto_now_add=True)
    restored_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey('InternalUser', on_delete=models.SET_NULL, null=True, related_name='soft_deletes')
    restored_by = models.ForeignKey('InternalUser', on_delete=models.SET_NULL, null=True, related_name='restores')

    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
        ]

class JobOffer(models.Model):
    title = models.CharField(max_length=128)
    description = models.TextField()
    skill_level = models.CharField(max_length=64, choices=SENIORITY_LEVEL_CHOICES)
    tags = models.CharField(max_length=255)
    salary_offer = models.IntegerField(default=0, validators=[MinValueValidator(0)], blank=True)
    location = models.CharField(max_length=255, blank=True)
    work_mode = models.CharField(max_length=20, blank=True, choices=WORK_MODE_CHOICES)
    url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    company = models.ForeignKey('Company', on_delete=models.CASCADE, related_name='job_offers')
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    active = SoftDeleteManager()
    deleted = SoftDeletedManager()

    def soft_delete(self, user=None):
        return SoftDeleteBehavior.soft_delete(self, user=user)

    def restore(self, user=None):
        return SoftDeleteBehavior.restore(self, user=user)

    def __str__(self):
        return self.title


class Company(models.Model):
    name = models.CharField(max_length=128)
    company_bio = models.TextField(blank=True)
    company_website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    active = SoftDeleteManager()
    deleted = SoftDeletedManager()

    def __str__(self):
        return self.name


class InternalUser(models.Model):
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128, blank=True)
    email = models.CharField(max_length=128, blank=False, null=False, unique=True)
    skill_level = models.CharField(max_length=64, choices=SENIORITY_LEVEL_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    django_user = models.OneToOneField('User', on_delete=models.CASCADE)
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    active = SoftDeleteManager()
    deleted = SoftDeletedManager()

    def soft_delete(self, user=None):
        return SoftDeleteBehavior.soft_delete(self, user=user)

    def restore(self, user=None):
        return SoftDeleteBehavior.restore(self, user=user)

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class JobApplication(models.Model):
    job_offer = models.ForeignKey('JobOffer', on_delete=models.CASCADE, related_name='job_applications')
    internal_user = models.ForeignKey('InternalUser', on_delete=models.CASCADE, related_name='job_applications')
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    status = models.IntegerField(default=0, db_index=True)
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    active = SoftDeleteManager()
    deleted = SoftDeletedManager()

    def __str__(self):
        return f'{self.job_offer.title} {self.status}'


class InternalUserSkillset(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    internal_user = ForeignKey('InternalUser', on_delete=models.CASCADE, related_name='personal_skillset')

    active = SoftDeleteManager()
    deleted = SoftDeletedManager()

    def __str__(self):
        return f'{self.internal_user.full_name} - {self.core_skills}'


class CoreSkill(models.Model):
    name = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    personal_skills = models.ManyToManyField('InternalUserSkillset', related_name='core_skills')

    active = SoftDeleteManager()
    deleted = SoftDeletedManager()

    def __str__(self):
        return f'{self.name}'


class SecondarySkill(models.Model):
    name = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    personal_skills = models.ManyToManyField('InternalUserSkillset', related_name='secondary_skills')

    active = SoftDeleteManager()
    deleted = SoftDeletedManager()

    def __str__(self):
        return f'{self.name}'


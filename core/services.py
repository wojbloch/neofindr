from django.db.models import QuerySet

from core.models import InternalUser, JobApplication


class JobApplicationService:
    def __init__(self, internal_user_model=InternalUser, job_application_model=JobApplication):
        self.internal_user = internal_user_model
        self.job_application = job_application_model

    def get_applications_per_user(self, internal_user_id: int) -> QuerySet[JobApplication]:
        return self.job_application.active.filter(internal_user_id=internal_user_id)

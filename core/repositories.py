from typing import TypeVar, Optional, Generic, Type, List, Iterable
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db.models import QuerySet, Model
from django.utils import timezone
from core.models import InternalUser, User
from utils.model_behavior import SoftDeleteBehavior as SDB

# will actually just leave CRUD generics + only custom logic will land here

T = TypeVar('T', bound=Model)

class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T]):
        self.model = model

    def get_all(self) -> QuerySet[T]:
        return self.model.objects.filter(is_deleted=False)

    def get_by_id(self, obj_id: int) -> T:
        try:
            return self.model.objects.get(is_deleted=False, id=obj_id)
        except MultipleObjectsReturned:
            raise MultipleObjectsReturned(f"More than one instances found with ID {obj_id}")
        except ObjectDoesNotExist:
            raise ObjectDoesNotExist(f"Object with ID {obj_id} does not exist")

    def create(self, **kwargs) -> T:
        return self.model.objects.create(**kwargs)

    def bulk_create(self, objects_list: Iterable[Type[T]]) -> List[T]:
        return self.model.objects.bulk_create(objects_list)

    def update(self, obj_id: int, **kwargs) -> Optional[T]:
        obj = self.get_by_id(obj_id)
        for key, value in kwargs.items():
            setattr(obj, key, value)
        obj.save()
        return obj

    def bulk_update(self, objects_list: Iterable[Type[T]], fields: List[str]) -> None:
        self.model.objects.bulk_update(objects_list, fields)

    def delete(self, obj_id: int, user: Optional[User] = None) -> T:
        try:
            if hasattr(self.model, 'active'):
                obj = self.model.active.get(pk=obj_id)
            else:
                obj = self.model.objects.get(is_deleted=False, pk=obj_id)
        except MultipleObjectsReturned:
            raise MultipleObjectsReturned(f"More than one object found with ID {obj_id}")
        except ObjectDoesNotExist:
            raise ObjectDoesNotExist(f"Object with ID {obj_id} does not exist")
        return SDB.soft_delete(obj, user=user)

    def restore(self, obj_id: int, user: Optional[User] = None) -> T:
        try:
            if hasattr(self.model, 'deleted'):
                obj = self.model.deleted.get(pk=obj_id)
            else:
                obj = self.model.objects.get(is_deleted=True, pk=obj_id)
        except MultipleObjectsReturned:
            raise MultipleObjectsReturned(f"More than one user found with ID {obj_id}")
        except ObjectDoesNotExist:
            raise ObjectDoesNotExist(f"Object with ID {obj_id} does not exist")
        return SDB.restore(obj, user=user)


class InternalUserRepository:
    def __init__(self, internal_user_model=InternalUser):
        self.internal_user_model = internal_user_model

    def get_all(self) -> QuerySet[InternalUser]:
        return self.internal_user_model.active.all()

    def get_all_deleted(self) -> QuerySet[InternalUser]:
        return self.internal_user_model.deleted.all()

    def get_by_id(self, internal_user_id: int) -> InternalUser:
        try:
            return self.internal_user_model.active.get(pk=internal_user_id)
        except MultipleObjectsReturned:
            raise MultipleObjectsReturned(f"More than one user found with ID {internal_user_id}")
        except ObjectDoesNotExist:
            raise ObjectDoesNotExist(f"Object with ID {internal_user_id} does not exist")

    def get_deleted_by_id(self, internal_user_id: int) -> InternalUser:
        try:
            return self.internal_user_model.deleted.get(pk=internal_user_id)
        except MultipleObjectsReturned:
            raise MultipleObjectsReturned(f"More than one user found with ID {internal_user_id}")

    def create(self, **kwargs) -> InternalUser:
        return self.internal_user_model.objects.create(**kwargs)

    def update(self, internal_user_id: int, **kwargs) -> InternalUser:
        internal_user = self.get_by_id(internal_user_id)
        for k, v in kwargs.items():
            setattr(internal_user, k, v)
        internal_user.save()
        return internal_user

    def delete(self, internal_user_id: int, user: Optional[User] = None) -> InternalUser:
        try:
            internal_user = self.internal_user_model.active.get(pk=internal_user_id)
        except MultipleObjectsReturned:
            raise MultipleObjectsReturned(f"More than one user found with ID {internal_user_id}")
        deleted = SDB.soft_delete(internal_user, user=user)
        return deleted

    def restore(self, internal_user_id: int, user: Optional[User] = None) -> InternalUser:
        try:
            internal_user = self.internal_user_model.deleted.get(pk=internal_user_id)
        except MultipleObjectsReturned:
            raise MultipleObjectsReturned(f"More than one user found with ID {internal_user_id}")
        restored = SDB.restore(internal_user, user=user)
        return restored

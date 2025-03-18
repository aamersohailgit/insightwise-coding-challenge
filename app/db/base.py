from typing import Dict, List, Any, Optional, TypeVar, Generic, Type
from bson import ObjectId

T = TypeVar('T')

class BaseRepository(Generic[T]):
    model_class: Type[T]

    def find_one(self, id: str) -> Optional[T]:
        return self.model_class.objects(id=ObjectId(id)).first()

    def find_all(self) -> List[T]:
        return list(self.model_class.objects.all())

    def create(self, data: Dict[str, Any]) -> T:
        instance = self.model_class(**data)
        instance.save()
        return instance

    def update(self, id: str, data: Dict[str, Any]) -> Optional[T]:
        instance = self.find_one(id)
        if not instance:
            return None

        for key, value in data.items():
            setattr(instance, key, value)

        instance.save()
        return instance

    def delete(self, id: str) -> bool:
        instance = self.find_one(id)
        if not instance:
            return False

        instance.delete()
        return True

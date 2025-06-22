from django.db import models
from django.contrib.auth.models import AbstractUser
from typing import Optional, Any


class User(AbstractUser):
    class Meta:
        db_table = 'users'
        verbose_name = "Użytkownik"
        verbose_name_plural = "Użytkownicy"

    def __str__(self) -> str:
        return self.username

    def save(self, *args: Any, **kwargs: Any) -> None:
        super().save(*args, **kwargs)

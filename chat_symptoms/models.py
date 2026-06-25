from django.db import models

# Create your models here.
from django.db import models

class NameChoice(models.Model):
    key = models.CharField(max_length=100, unique=True)  # The value stored in the database
    display = models.CharField(max_length=255)          # The human-readable name

    def __str__(self):
        return self.display


class ModelConfiguration(models.Model):
    name = models.CharField(max_length=255)             # Choices will be populated dynamically
    sector_id = models.PositiveIntegerField()
    role_id = models.PositiveIntegerField()
    model_id = models.PositiveIntegerField()
    save_chat = models.BooleanField(default=True)

    class Meta:
        unique_together = ('sector_id', 'role_id', 'model_id')
        verbose_name = "Model Configuration"
        verbose_name_plural = "Model Configurations"

    def __str__(self):
        return f"{self.name} (sector_id={self.sector_id}, role_id={self.role_id}, model_id={self.model_id})"
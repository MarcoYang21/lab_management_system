#equipment>models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils import timezone

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', '管理員'),
        ('user', '一般使用者'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

class Equipment(models.Model):
    name = models.CharField(max_length=100, verbose_name="設備名稱")
    description = models.TextField(blank=True, null=True, verbose_name="設備描述")
    is_available = models.BooleanField(default=True, verbose_name="是否可用")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "設備列表"
        verbose_name_plural = "設備列表"
        permissions = [
            ("can_view_all_reservations", "Can view all reservations"),
            ("can_manage_equipment", "Can manage equipment"),
    ]

class AdditionalEquipment(models.Model):
    name = models.CharField(max_length=50, verbose_name="附加設備名稱")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "增加設備"
        verbose_name_plural = "增加設備"
        permissions = [
            ("can_view_all_reservations", "Can view all reservations"),
            ("can_manage_equipment", "Can manage equipment"),
    ]

class Reservation(models.Model):
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, verbose_name="主要設備")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="預約用戶")
    test_name = models.CharField(max_length=100, verbose_name="測試名稱")
    temperature = models.FloatField(verbose_name="溫度")
    start_time = models.DateTimeField(verbose_name="開始時間")
    end_time = models.DateTimeField(verbose_name="結束時間")
    additional_equipment = models.ManyToManyField(AdditionalEquipment, blank=True, verbose_name="附加設備")
    notified = models.BooleanField(default=False, verbose_name="是否已通知")

    def __str__(self):
        return f"{self.equipment.name} - {self.test_name} by {self.user.username}"

    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError("結束時間必須晚於開始時間")

        # 檢查時間衝突
        overlapping_reservations = Reservation.objects.filter(
            equipment=self.equipment,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        ).exclude(pk=self.pk)

        if overlapping_reservations.exists():
            raise ValidationError("此時間段已被預約")

    class Meta:
        verbose_name = "預約"
        verbose_name_plural = "預約"
        permissions = [
            ("can_view_all_reservations", "Can view all reservations"),
            ("can_manage_equipment", "Can manage equipment"),
    ]
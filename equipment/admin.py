# equipment>admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Equipment, AdditionalEquipment, Reservation
from django.core.cache import cache
from django.db.models import Count
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponseRedirect
from django.urls import path, reverse

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('個人信息', {'fields': ('role',)}),
        ('權限', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('username', 'email')
    ordering = ('username',)

class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_available')
    list_filter = ('is_available',)
    search_fields = ('name', 'description')
    actions = ['mark_as_unavailable']

    def mark_as_unavailable(self, request, queryset):
        queryset.update(is_available=False)
    mark_as_unavailable.short_description = "將選中的設備標記為不可用"

class AdditionalEquipmentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class ReservationAdmin(admin.ModelAdmin):
    list_display = ('user', 'equipment', 'test_name', 'temperature', 'start_time', 'end_time', 'notified')
    list_filter = ('notified',)
    search_fields = ('user__username', 'equipment__name', 'test_name')
    filter_horizontal = ('additional_equipment',)
    actions = ['mark_as_notified']

    def mark_as_notified(self, request, queryset):
        queryset.update(notified=True)
    mark_as_notified.short_description = "將選中的預約標記為已通知"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('notify/<int:reservation_id>/', self.admin_site.admin_view(self.notify_reservation), name='notify_reservation'),
        ]
        return custom_urls + urls

    def notify_reservation(self, request, reservation_id):
        reservation = Reservation.objects.get(id=reservation_id)
        reservation.notified = True
        reservation.save()
        self.message_user(request, f"預約 {reservation_id} 已標記為已通知")
        return HttpResponseRedirect("../")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.has_perm('equipment.can_view_all_reservations'):
            return qs
        return qs.filter(user=request.user)

class CustomAdminSite(admin.AdminSite):
    site_header = _("實驗室設備管理系統")
    site_title = _("實驗室設備管理")
    index_title = _("歡迎來到實驗室設備管理系統")

    def get_app_list(self, request):
        app_list = super().get_app_list(request)
        app_list += [
            {
                'name': 'View Site',
                'app_label': 'view_site',
                'models': [{
                    'name': 'View Site',
                    'object_name': 'view_site',
                    'admin_url': reverse('home'),
                    'view_only': True,
                }],
            }
        ]
        return app_list

    def index(self, request, extra_context=None):
        # 緩存統計數據，每5分鐘更新一次
        stats = cache.get('admin_stats')
        if not stats:
            stats = {
                'total_users': User.objects.count(),
                'total_equipment': Equipment.objects.count(),
                'total_reservations': Reservation.objects.count(),
                'equipment_available': dict(Equipment.objects.values_list('is_available').annotate(count=Count('is_available'))),
                'reservation_notified': dict(Reservation.objects.values_list('notified').annotate(count=Count('notified'))),
            }
            cache.set('admin_stats', stats, 300)  # 緩存5分鐘

        extra_context = extra_context or {}
        extra_context.update(stats)
        return super().index(request, extra_context)

admin_site = CustomAdminSite(name='custom_admin')

# 重新註冊所有模型到自定義管理站點
admin_site.register(User, CustomUserAdmin)
admin_site.register(Equipment, EquipmentAdmin)
admin_site.register(AdditionalEquipment, AdditionalEquipmentAdmin)
admin_site.register(Reservation, ReservationAdmin)

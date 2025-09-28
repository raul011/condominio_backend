
from django.contrib import admin


from .models import DeviceToken

@admin.register(DeviceToken)
class DeviceTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'token_preview', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['user__username', 'user__email', 'token']
    readonly_fields = ['created_at']
    
    def token_preview(self, obj):
        return f"{obj.token[:20]}..." if obj.token else ""
    token_preview.short_description = 'Token'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
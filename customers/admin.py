from django.contrib import admin
from .models import Profile, Customer


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone', 'company_name', 'created_at')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__email', 'phone', 'company_name')


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'distributor', 'phone', 'email', 'city', 'status', 'created_at')
    list_filter = ('status', 'city', 'state')
    search_fields = ('name', 'email', 'phone', 'company_name', 'gst_number')
    autocomplete_fields = ('distributor',)
    list_per_page = 25

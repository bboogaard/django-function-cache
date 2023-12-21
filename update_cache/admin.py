import sys

from django.contrib import admin
from django.http import Http404
from django.template.defaultfilters import truncatechars

from .models import CacheEntry


class CacheEntryAdmin(admin.ModelAdmin):
    list_display = (
        'cache_key', 'function', 'calling_args', 'truncated_value', 'expires', 'has_expired'
    )
    list_per_page = sys.maxsize
    sortable_by = ()
    actions = ('invalidate', 'delete')

    @admin.action(description='Invalidate cache entries')
    def invalidate(self, request, queryset):
        num_invalidated = 0
        selected = request.POST.getlist('_selected_action')
        for obj in queryset:
            cached_function = obj.cached_function
            if cached_function is not None and obj.cache_key in selected:
                cached_function.invalidate(obj.cache_key)
                num_invalidated += 1
        entry_bit = 'cache entry' if num_invalidated == 1 else 'cache entries'
        self.message_user(request, f'Invalidated {num_invalidated} {entry_bit}')

    @admin.action(description='Delete cache entries')
    def delete(self, request, queryset):
        num_deleted = 0
        selected = request.POST.getlist('_selected_action')
        for obj in queryset:
            cached_function = obj.cached_function
            if cached_function is not None and obj.cache_key in selected:
                cached_function.delete(obj.cache_key)
                num_deleted += 1
        entry_bit = 'cache entry' if num_deleted == 1 else 'cache entries'
        self.message_user(request, f'Deleted {num_deleted} {entry_bit}')

    def get_object(self, request, object_id, from_field=None):
        cache_entries = CacheEntry.objects.all()
        obj = next(filter(lambda c: c.pk == object_id, cache_entries), None)
        if obj is None:
            raise Http404()
        return obj

    @admin.display(description='Value')
    def truncated_value(self, obj):
        return truncatechars(obj.value, 25)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(CacheEntry, CacheEntryAdmin)

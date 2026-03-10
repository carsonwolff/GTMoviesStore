from django.contrib import admin
from django.db.models import Count, Sum
from django.template.response import TemplateResponse
from django.urls import path
from cart.models import Item
from .models import Profile
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

class ProfileInLine(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'

class ProfileAdmin(UserAdmin):
    inlines = [ProfileInLine]
    list_display = UserAdmin.list_display + ('get_movie_count', )
    def get_movie_count(self, object):
        try:
            return object.profile.movie_count
        except Profile.DoesNotExist:
            return 0
    get_movie_count.short_description = 'Movies bought by User'

admin.site.unregister(User)
admin.site.register(User, ProfileAdmin)


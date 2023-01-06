from django.contrib import admin

from goals.models import Goal
from goals.models import GoalCategory
from goals.models import GoalComment


class GoalCategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "created", "updated")
    search_fields = ("title", "user")


admin.site.register(GoalCategory, GoalCategoryAdmin)
admin.site.register(Goal)
admin.site.register(GoalComment)

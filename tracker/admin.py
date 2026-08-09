from django.contrib import admin
from .models import Project, Issue, Comment


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'project')
    search_fields = ('title', 'description')
    inlines = [CommentInline]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('issue', 'content', 'created_at')
    list_filter = ('created_at',)

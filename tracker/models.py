from django.db import models


class Project(models.Model):
    """Represents a software project containing issues."""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Issue(models.Model):
    """Represents a task or bug within a Project."""

    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
    ]

    title = models.CharField(max_length=300)
    description = models.TextField(blank=True, default='')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='todo',
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='issues',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_status_display_label(self):
        """Return the human-readable status label."""
        return dict(self.STATUS_CHOICES).get(self.status, self.status)


class Comment(models.Model):
    """A comment on an Issue."""
    content = models.TextField()
    issue = models.ForeignKey(
        Issue,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Comment on "{self.issue.title}" at {self.created_at}'

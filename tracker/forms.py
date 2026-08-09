from django import forms
from .models import Issue, Comment


class IssueForm(forms.ModelForm):
    """Form for creating a new issue."""

    class Meta:
        model = Issue
        fields = ['title', 'description', 'status']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Issue title',
                'id': 'id_issue_title',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Describe the issue...',
                'rows': 4,
                'id': 'id_issue_description',
            }),
            'status': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_issue_status',
            }),
        }


class CommentForm(forms.ModelForm):
    """Form for adding a comment to an issue."""

    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Write a comment...',
                'rows': 3,
                'id': 'id_comment_content',
            }),
        }

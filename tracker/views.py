from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST, require_GET

from .models import Project, Issue, Comment
from .forms import IssueForm, CommentForm


def _is_htmx(request):
    """Check if the request is an HTMX (enhanced) request."""
    return request.headers.get('HX-Request') == 'true'


@require_GET
def healthz(request):
    """Simple healthcheck endpoint used by the Docker healthcheck."""
    return JsonResponse({'status': 'ok'})


# ── Project Views ───────────────────────────────────────────────────

@require_GET
def project_list(request):
    """Display a list of all projects."""
    projects = Project.objects.all()
    return render(request, 'tracker/project_list.html', {
        'projects': projects,
    })


@require_GET
def project_board(request, project_id):
    """
    Display a Kanban-style board for a project, with issues grouped
    by status (To Do, In Progress, Done).
    """
    project = get_object_or_404(Project, pk=project_id)
    issues = project.issues.all()

    todo_issues = issues.filter(status='todo')
    in_progress_issues = issues.filter(status='in_progress')
    done_issues = issues.filter(status='done')

    issue_form = IssueForm()

    return render(request, 'tracker/project_board.html', {
        'project': project,
        'todo_issues': todo_issues,
        'in_progress_issues': in_progress_issues,
        'done_issues': done_issues,
        'issue_form': issue_form,
    })


# ── Issue Views ─────────────────────────────────────────────────────

@require_POST
def create_issue(request, project_id):
    """
    Create a new issue for a project.

    Standard request: redirects to the project board.
    Enhanced request: returns the new issue card partial.
    """
    project = get_object_or_404(Project, pk=project_id)
    form = IssueForm(request.POST)

    if form.is_valid():
        issue = form.save(commit=False)
        issue.project = project
        issue.save()

        if _is_htmx(request):
            return render(request, 'tracker/partials/_issue_card.html', {
                'issue': issue,
            })
        return redirect('project_board', project_id=project.id)

    # Form invalid — re-render with errors
    if _is_htmx(request):
        return render(request, 'tracker/partials/_issue_form.html', {
            'issue_form': form,
            'project': project,
        })
    # For standard request, re-render the full board with the form errors
    issues = project.issues.all()
    return render(request, 'tracker/project_board.html', {
        'project': project,
        'todo_issues': issues.filter(status='todo'),
        'in_progress_issues': issues.filter(status='in_progress'),
        'done_issues': issues.filter(status='done'),
        'issue_form': form,
    })


@require_GET
def issue_detail(request, issue_id):
    """Display issue details with comments and a comment form."""
    issue = get_object_or_404(Issue, pk=issue_id)
    comments = issue.comments.all()
    comment_form = CommentForm()

    return render(request, 'tracker/issue_detail.html', {
        'issue': issue,
        'comments': comments,
        'comment_form': comment_form,
    })


@require_POST
def update_issue_status(request, issue_id):
    """
    Update an issue's status.

    Standard request: redirects back to the project board (302).
    Enhanced request: returns the updated issue card partial (200).
    """
    issue = get_object_or_404(Issue, pk=issue_id)
    new_status = request.POST.get('status')

    if new_status in dict(Issue.STATUS_CHOICES):
        issue.status = new_status
        issue.save()

    if _is_htmx(request):
        return render(request, 'tracker/partials/_issue_card.html', {
            'issue': issue,
        })

    return redirect('project_board', project_id=issue.project.id)


# ── Comment Views ───────────────────────────────────────────────────

@require_POST
def add_comment(request, issue_id):
    """
    Add a comment to an issue.

    Standard request: redirects back to the issue detail page (302).
    Enhanced request: returns the new comment partial (200).
    """
    issue = get_object_or_404(Issue, pk=issue_id)
    form = CommentForm(request.POST)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.issue = issue
        comment.save()

        if _is_htmx(request):
            return render(request, 'tracker/partials/_comment.html', {
                'comment': comment,
            })
        return redirect('issue_detail', issue_id=issue.id)

    # Form invalid
    if _is_htmx(request):
        return render(request, 'tracker/partials/_comment_form.html', {
            'comment_form': form,
            'issue': issue,
        })
    # Re-render full page with errors
    comments = issue.comments.all()
    return render(request, 'tracker/issue_detail.html', {
        'issue': issue,
        'comments': comments,
        'comment_form': form,
    })

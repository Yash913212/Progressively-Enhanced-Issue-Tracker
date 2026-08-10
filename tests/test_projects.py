from django.test import TestCase
from django.urls import reverse

from tracker.models import Project, Issue


class ProjectViewTests(TestCase):
    """Standard (no-JS) tests for project views."""

    def setUp(self):
        self.project = Project.objects.create(
            name='Test Project',
            description='A project used in tests.',
        )
        self.project.issues.create(
            title='Todo issue',
            description='First task',
            status='todo',
        )
        self.project.issues.create(
            title='In progress issue',
            description='Second task',
            status='in_progress',
        )
        self.project.issues.create(
            title='Done issue',
            description='Third task',
            status='done',
        )

    def test_project_list_returns_full_page(self):
        response = self.client.get(reverse('project_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<html')
        self.assertContains(response, 'Test Project')

    def test_project_board_groups_issues_by_status(self):
        projects = Project.objects.order_by('pk')
        url = reverse('project_board', args=[projects[0].id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<html')
        self.assertContains(response, '<body>')
        for label in ('To Do', 'In Progress', 'Done'):
            self.assertContains(response, label)
        for title in ('Todo issue', 'In progress issue', 'Done issue'):
            self.assertContains(response, title)

    def test_project_board_unknown_project_404(self):
        response = self.client.get(reverse('project_board', args=[9999]))
        self.assertEqual(response.status_code, 404)

    def test_project_board_requires_get(self):
        response = self.client.post(reverse('project_board', args=[self.project.id]))
        self.assertEqual(response.status_code, 405)

    def test_healthz_endpoint(self):
        response = self.client.get(reverse('healthz'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'ok'})

    def test_project_list_empty(self):
        """Project list renders without errors when there are no projects."""
        Project.objects.all().delete()
        response = self.client.get(reverse('project_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<html')

    def test_issue_detail_unknown_returns_404(self):
        response = self.client.get(reverse('issue_detail', args=[99999]))
        self.assertEqual(response.status_code, 404)
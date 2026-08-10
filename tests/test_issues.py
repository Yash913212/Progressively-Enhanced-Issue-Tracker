from django.test import TestCase
from django.urls import reverse

from tracker.models import Project, Issue


class IssueFormTests(TestCase):
    """Tests for the standard (no-JS) issue creation flow."""

    def setUp(self):
        self.project = Project.objects.create(
            name='Test Project',
            description='Project for issue tests.',
        )
        self.url = reverse('create_issue', args=[self.project.id])

    def test_create_issue_standard_redirects(self):
        initial_count = Issue.objects.filter(project=self.project).count()

        response = self.client.post(self.url, {
            'title': 'New issue',
            'description': 'A brand new issue.',
            'status': 'todo',
        })

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('project_board', args=[self.project.id]))
        self.assertEqual(
            Issue.objects.filter(project=self.project).count(),
            initial_count + 1,
        )
        new_issue = Issue.objects.get(title='New issue')
        self.assertEqual(new_issue.project, self.project)
        self.assertEqual(new_issue.status, 'todo')

    def test_create_issue_invalid_rerenders_full_page(self):
        response = self.client.post(self.url, {
            'title': '',
            'description': 'Missing title -> invalid.',
            'status': 'todo',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<html')

    def test_create_issue_get_not_allowed(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_create_issue_htmx_returns_partial(self):
        response = self.client.post(self.url, {
            'title': 'Ajax issue',
            'description': 'Created via HTMX.',
            'status': 'in_progress',
        }, HTTP_HX_REQUEST='true')

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, '<html>')
        self.assertNotContains(response, '<body>')
        self.assertContains(response, 'Ajax issue')
        self.assertTemplateUsed(response, 'tracker/partials/_issue_card.html')
        self.assertTrue(Issue.objects.filter(title='Ajax issue').exists())

    def test_create_issue_htmx_invalid_rerenders_partial(self):
        """HTMX invalid submission returns the form partial, not a full page."""
        response = self.client.post(self.url, {
            'title': '',  # blank title → invalid
            'status': 'todo',
        }, HTTP_HX_REQUEST='true')

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, '<html>')
        self.assertTemplateUsed(response, 'tracker/partials/_issue_form.html')
        self.assertFalse(Issue.objects.filter(project=self.project).exists())



class IssueStatusTests(TestCase):
    """Tests for the status update flow in both request modes."""

    def setUp(self):
        project = Project.objects.create(name='Test Project')
        self.issue = project.issues.create(
            title='Status issue',
            status='todo',
        )
        self.url = reverse('update_issue_status', args=[self.issue.id])
        self.board_url = reverse('project_board', args=[project.id])

    def test_update_status_standard_redirects(self):
        self.issue.refresh_from_db()
        self.assertEqual(self.issue.status, 'todo')

        response = self.client.post(self.url, {'status': 'done'})

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.board_url)

        self.issue.refresh_from_db()
        self.assertEqual(self.issue.status, 'done')

    def test_update_status_htmx_returns_partial(self):
        response = self.client.post(self.url, {'status': 'in_progress'}, HTTP_HX_REQUEST='true')

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, '<html>')
        self.assertNotContains(response, '<body>')
        self.assertContains(response, f'id="issue-{self.issue.id}"')
        self.assertTemplateUsed(response, 'tracker/partials/_issue_card.html')

        self.issue.refresh_from_db()
        self.assertEqual(self.issue.status, 'in_progress')

    def test_same_endpoint_two_request_modes(self):
        # Request 1: standard request -> 302 redirect
        response_standard = self.client.post(self.url, {'status': 'in_progress'})
        self.assertEqual(response_standard.status_code, 302)

        # Request 2: enhanced request on the same issue -> 200 partial
        response_enhanced = self.client.post(
            self.url,
            {'status': 'done'},
            HTTP_HX_REQUEST='true',
        )
        self.assertEqual(response_enhanced.status_code, 200)
        self.assertNotContains(response_enhanced, '<html>')
        self.assertContains(response_enhanced, 'id="issue-%d"' % self.issue.id)
        self.assertTemplateUsed(response_enhanced, 'tracker/partials/_issue_card.html')

        self.issue.refresh_from_db()
        self.assertEqual(self.issue.status, 'done')

    def test_invalid_status_ignored(self):
        response = self.client.post(self.url, {'status': 'not-a-status'})
        self.assertEqual(response.status_code, 302)
        self.issue.refresh_from_db()
        self.assertEqual(self.issue.status, 'todo')

    def test_update_status_changes_updated_at(self):
        """Saving a new status must bump the updated_at timestamp."""
        import time
        original_updated_at = self.issue.updated_at
        time.sleep(0.05)  # Ensure clock advances
        self.client.post(self.url, {'status': 'done'})
        self.issue.refresh_from_db()
        self.assertGreater(self.issue.updated_at, original_updated_at)
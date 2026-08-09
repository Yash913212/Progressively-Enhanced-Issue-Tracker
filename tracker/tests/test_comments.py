from django.test import TestCase
from django.urls import reverse

from tracker.models import Project, Comment


class CommentTests(TestCase):
    """Tests for the comment flow in both standard and enhanced modes."""

    def setUp(self):
        project = Project.objects.create(name='Test Project')
        self.issue = project.issues.create(title='Issue with comments')
        self.url = reverse('add_comment', args=[self.issue.id])
        self.detail_url = reverse('issue_detail', args=[self.issue.id])

    def test_issue_detail_returns_full_page(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<html>')
        self.assertContains(response, 'Issue with comments')

    def test_add_comment_standard_redirects(self):
        initial_count = Comment.objects.filter(issue=self.issue).count()

        response = self.client.post(self.url, {'content': 'A standard comment.'})

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.detail_url)
        self.assertEqual(Comment.objects.filter(issue=self.issue).count(), initial_count + 1)

    def test_add_comment_htmx_returns_partial(self):
        response = self.client.post(
            self.url,
            {'content': 'An enhanced comment.'},
            HTTP_HX_REQUEST='true',
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, '<html>')
        self.assertNotContains(response, '<body>')
        self.assertContains(response, 'An enhanced comment.')
        self.assertTemplateUsed(response, 'tracker/partials/_comment.html')

        comment = Comment.objects.get(content='An enhanced comment.')
        self.assertEqual(comment.issue, self.issue)

    def test_add_comment_invalid_rerenders_full_page(self):
        response = self.client.post(self.url, {'content': ''})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<html>')

    def test_add_comment_get_not_allowed(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)
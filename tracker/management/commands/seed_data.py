"""
Management command to seed the database with sample data.
Idempotent — only seeds if no projects exist.
"""

from django.core.management.base import BaseCommand
from tracker.models import Project, Issue, Comment


class Command(BaseCommand):
    help = 'Seeds the database with sample projects, issues, and comments.'

    def handle(self, *args, **options):
        if Project.objects.exists():
            self.stdout.write(self.style.WARNING(
                'Database already contains data. Skipping seed.'
            ))
            return

        self.stdout.write('Seeding database...')

        # ── Project 1: E-Commerce Platform ──────────────────────────
        p1 = Project.objects.create(
            name='E-Commerce Platform',
            description='A modern online shopping platform with payment integration, '
                        'product catalog, and order management.',
        )
        i1 = Issue.objects.create(
            project=p1,
            title='Implement shopping cart persistence',
            description='Cart items should be saved to the database so users can '
                        'resume their session across devices.',
            status='todo',
        )
        Issue.objects.create(
            project=p1,
            title='Add Stripe payment gateway',
            description='Integrate Stripe Checkout for credit card and Apple Pay '
                        'support on the checkout page.',
            status='todo',
        )
        Issue.objects.create(
            project=p1,
            title='Design product detail page',
            description='Create responsive product detail page with image gallery, '
                        'size selector, and reviews section.',
            status='in_progress',
        )
        i4 = Issue.objects.create(
            project=p1,
            title='Set up CI/CD pipeline',
            description='Configure GitHub Actions to run tests and deploy to '
                        'staging on every push to main.',
            status='done',
        )
        Issue.objects.create(
            project=p1,
            title='Implement user authentication',
            description='Add login, registration, and password reset flows using '
                        'Django allauth.',
            status='in_progress',
        )
        Comment.objects.create(
            issue=i1,
            content='We should consider using localStorage as a fallback for '
                    'anonymous users.',
        )
        Comment.objects.create(
            issue=i1,
            content='Good point — let\'s also sync the cart when the user logs in.',
        )
        Comment.objects.create(
            issue=i4,
            content='Pipeline is live! Tests run in ~3 minutes.',
        )

        # ── Project 2: Task Management API ──────────────────────────
        p2 = Project.objects.create(
            name='Task Management API',
            description='A RESTful API for task management with team collaboration '
                        'features, built with Django REST Framework.',
        )
        Issue.objects.create(
            project=p2,
            title='Design REST API schema',
            description='Document the API endpoints, request/response formats, and '
                        'authentication strategy using OpenAPI 3.0.',
            status='done',
        )
        i7 = Issue.objects.create(
            project=p2,
            title='Implement task CRUD endpoints',
            description='Create, read, update, and delete operations for tasks with '
                        'proper serialization and validation.',
            status='in_progress',
        )
        Issue.objects.create(
            project=p2,
            title='Add WebSocket notifications',
            description='Real-time notifications when tasks are assigned or '
                        'completed using Django Channels.',
            status='todo',
        )
        Issue.objects.create(
            project=p2,
            title='Write API integration tests',
            description='Comprehensive test suite covering all endpoints with '
                        'both valid and invalid payloads.',
            status='todo',
        )
        Comment.objects.create(
            issue=i7,
            content='Serializers are done. Working on viewsets now.',
        )

        # ── Project 3: Developer Portfolio ──────────────────────────
        p3 = Project.objects.create(
            name='Developer Portfolio',
            description='A personal portfolio website showcasing projects, blog '
                        'posts, and professional experience.',
        )
        Issue.objects.create(
            project=p3,
            title='Create responsive landing page',
            description='Hero section with animated gradient background, intro '
                        'text, and call-to-action button.',
            status='done',
        )
        Issue.objects.create(
            project=p3,
            title='Build project showcase section',
            description='Grid layout displaying project cards with screenshots, '
                        'tech stack badges, and links.',
            status='in_progress',
        )
        Issue.objects.create(
            project=p3,
            title='Add dark mode toggle',
            description='Implement a theme switcher that respects prefers-color-scheme '
                        'and saves preference to localStorage.',
            status='todo',
        )
        Issue.objects.create(
            project=p3,
            title='Set up contact form',
            description='Contact form with email notifications using SendGrid and '
                        'spam protection via reCAPTCHA.',
            status='todo',
        )
        Issue.objects.create(
            project=p3,
            title='Optimize Lighthouse score',
            description='Achieve 90+ scores across all Lighthouse categories: '
                        'Performance, Accessibility, Best Practices, SEO.',
            status='in_progress',
        )

        self.stdout.write(self.style.SUCCESS(
            f'Successfully seeded: {Project.objects.count()} projects, '
            f'{Issue.objects.count()} issues, {Comment.objects.count()} comments.'
        ))

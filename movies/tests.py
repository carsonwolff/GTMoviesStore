from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from cart.models import Item, Order
from movies.models import Movie, Review


class MovieInsightsAdminTests(TestCase):
    def setUp(self):
        self.staff_user = User.objects.create_user(
            username='adminuser',
            password='pass12345',
            is_staff=True,
            is_superuser=True,
        )
        self.normal_user = User.objects.create_user(
            username='normaluser',
            password='pass12345',
        )
        self.movie_one = Movie.objects.create(
            name='Movie One',
            price=10,
            description='Desc one',
            image='movie_images/movie1.jpg',
        )
        self.movie_two = Movie.objects.create(
            name='Movie Two',
            price=20,
            description='Desc two',
            image='movie_images/movie2.jpg',
        )
        self.url = reverse('admin:movies_movie_insights')

    def test_insights_requires_staff_access(self):
        self.client.force_login(self.normal_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_insights_renders_for_staff(self):
        self.client.force_login(self.staff_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_insights_same_movie_for_bought_and_reviewed(self):
        Review.objects.create(
            comment='Great',
            movie=self.movie_one,
            user=self.normal_user,
        )
        order = Order.objects.create(user=self.normal_user, total=10)
        Item.objects.create(
            order=order,
            movie=self.movie_one,
            price=10,
            quantity=1,
        )
        self.client.force_login(self.staff_user)
        response = self.client.get(self.url)
        self.assertEqual(response.context['most_bought']['movie__name'], 'Movie One')
        self.assertEqual(response.context['most_bought']['total_bought'], 1)
        self.assertEqual(response.context['most_reviewed']['movie__name'], 'Movie One')
        self.assertEqual(response.context['most_reviewed']['total_reviews'], 1)

    def test_insights_different_movies_for_bought_and_reviewed(self):
        Review.objects.create(
            comment='Review one',
            movie=self.movie_one,
            user=self.normal_user,
        )
        Review.objects.create(
            comment='Review two',
            movie=self.movie_one,
            user=self.staff_user,
        )
        order_one = Order.objects.create(user=self.normal_user, total=20)
        Item.objects.create(
            order=order_one,
            movie=self.movie_two,
            price=20,
            quantity=2,
        )
        order_two = Order.objects.create(user=self.normal_user, total=20)
        Item.objects.create(
            order=order_two,
            movie=self.movie_two,
            price=20,
            quantity=1,
        )
        self.client.force_login(self.staff_user)
        response = self.client.get(self.url)
        self.assertEqual(response.context['most_reviewed']['movie__name'], 'Movie One')
        self.assertEqual(response.context['most_reviewed']['total_reviews'], 2)
        self.assertEqual(response.context['most_bought']['movie__name'], 'Movie Two')
        self.assertEqual(response.context['most_bought']['total_bought'], 3)

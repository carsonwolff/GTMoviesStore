from django.contrib import admin
from django.db.models import Count, Sum
from django.template.response import TemplateResponse
from django.urls import path
from cart.models import Item
from .models import Movie, Review

class MovieAdmin(admin.ModelAdmin):
    ordering = ['name']
    search_fields = ['name']
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'insights/',
                self.admin_site.admin_view(self.insights_view),
                name='movies_movie_insights',
            ),
        ]
        return custom_urls + urls
    def insights_view(self, request):
        most_bought = (
            Item.objects.values('movie__name')
            .annotate(total_bought=Sum('quantity'))
            .order_by('-total_bought', 'movie__name')
            .first()
        )
        most_reviewed = (
            Review.objects.values('movie__name')
            .annotate(total_reviews=Count('id'))
            .order_by('-total_reviews', 'movie__name')
            .first()
        )
        context = dict(
            self.admin_site.each_context(request),
            title='Movie Insights',
            most_bought=most_bought,
            most_reviewed=most_reviewed,
        )
        return TemplateResponse(request, 'admin/movie_insights.html', context)

admin.site.register(Movie, MovieAdmin)
admin.site.register(Review)

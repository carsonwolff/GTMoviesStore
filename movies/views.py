from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review
from django.contrib.auth.decorators import login_required
from cart.models import Order, Item
from django.db.models import Count
from django.http import JsonResponse

# Create your views here.

def index(request):
    search_term = request.GET.get('search')
    if search_term:
        movies = Movie.objects.filter(name__icontains=search_term)
    else:
        movies = Movie.objects.all()
    template_data = {}
    template_data['title'] = 'Movies'
    template_data['movies'] = movies
    return render(request, 'movies/index.html',
                  {'template_data': template_data})

def show(request,id):
    movie = Movie.objects.get(id=id)
    reviews = Review.objects.filter(movie=movie)
    template_data = {}
    template_data['title'] = movie.name
    template_data['movie'] = movie
    template_data['reviews'] = reviews
    return render(request, 'movies/show.html', {'template_data': template_data})

@login_required
def create_review(request,id):
    if request.method == 'POST' and request.POST['comment'] != '':
        movie = Movie.objects.get(id=id)
        review = Review()
        review.comment = request.POST['comment']
        review.movie = movie
        review.user = request.user
        review.save()
        return redirect('movies.show', id=id)
    else: 
        return redirect('movies.show', id=id)

@login_required
def edit_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.user:
        return redirect('movies.show', id=id)
    if request.method == 'GET':
        template_data = {}
        template_data['title'] = 'Edit Review'
        template_data['review'] = review
        return render(request, 'movies/edit_review.html', {'template_data': template_data})
    elif request.method == 'POST'  and request.POST['comment'] != '':
        review = Review.objects.get(id=review_id)
        review.comment = request.POST['comment']
        review.save()
        return redirect('movies.show', id=id)
    else: 
        return redirect('movies.show', id=id)

@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    review.delete()
    return redirect('movies.show', id=id)

def map_view(request):
    template_data = {}
    template_data['title'] = 'Local Popularity Map'
    return render(request, 'movies/map.html', {'template_data': template_data})

def trending_movies_api(request):
    # Fetch items from orders that have location data
    # We will group by latitude and longitude and find the most popular movie at each location
    # In a real app we might cluster by region, but grouping by exact lat/lng or rounding is a simple start
    
    # We'll fetch all items linked to orders with location data
    items = Item.objects.filter(
        order__latitude__isnull=False, 
        order__longitude__isnull=False
    ).select_related('movie', 'order')
    
    # Create a dictionary to hold location-based movie counts
    location_counts = {}
    
    for item in items:
        # Round to 1 decimal place (~10km) to group nearby purchases
        lat = round(item.order.latitude, 1)
        lng = round(item.order.longitude, 1)
        loc_key = f"{lat},{lng}"
        
        if loc_key not in location_counts:
            location_counts[loc_key] = {
                'lat': lat,
                'lng': lng,
                'movies': {}
            }
            
        movie_id = item.movie.id
        if movie_id not in location_counts[loc_key]['movies']:
            location_counts[loc_key]['movies'][movie_id] = {
                'name': item.movie.name,
                'count': 0
            }
            
        location_counts[loc_key]['movies'][movie_id]['count'] += item.quantity

    # Determine the trending movie for each location group
    trending_data = []
    for loc_key, data in location_counts.items():
        if data['movies']:
            # Find movie with max count
            trending_movie = max(data['movies'].values(), key=lambda x: x['count'])
            trending_data.append({
                'lat': data['lat'],
                'lng': data['lng'],
                'trending_movie': trending_movie['name'],
                'purchase_count': trending_movie['count']
            })
            
    return JsonResponse({'locations': trending_data})

@login_required
def report_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    review.delete()
    return redirect('movies.show', id=id)
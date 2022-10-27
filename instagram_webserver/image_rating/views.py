from django.shortcuts import render
from django.views import generic
from .models import ImagesNew, FacesNew
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt




# Create your views here.

class IndexView(generic.ListView):
    model = ImagesNew
    template_name = 'image_rating/index.html'
    
    def get_queryset(self):
        return 


@csrf_exempt
def new_image(request, **kwargs):

    row_result = FacesNew.objects.filter(score=-1.0).order_by('?').first()

    filename = row_result.filename
    image_id = row_result.id
    root = f'/Users/briankelleher/Documents/Github/instagram-bot/'

    src = f'/static/{filename}'

    data = {
        'src': src,
        'image_id': image_id
    }
    return JsonResponse(data)



def get_stats(request):
    row_result = FacesNew.objects.all()

    stats_list = [
        {
            "number": 1,
            "stat": row_result.filter(score=1.0).count()
        },
        {
            "number": 2,
            "stat": row_result.filter(score=2.0).count()
        },
        {
            "number": 3,
            "stat": row_result.filter(score=3.0).count()
        },
        {
            "number": 4,
            "stat": row_result.filter(score=4.0).count()
        },
        {
            "number": 5,
            "stat": row_result.filter(score=5.0).count()
        },
        {
            "number": 6,
            "stat": row_result.filter(score=6.0).count()
        },
        {
            "number": 7,
            "stat": row_result.filter(score=7.0).count()
        },
        {
            "number": 8,
            "stat": row_result.filter(score=8.0).count()
        },
        {
            "number": 9,
            "stat": row_result.filter(score=9.0).count()
        },
        {
            "number": 10,
            "stat": row_result.filter(score=10.0).count()
        }
    ]

    data = {
        'stats_list': stats_list
    }

    return JsonResponse(data)


@csrf_exempt
def update(request, **kwargs):
    image_id = request.POST['image_id']
    image_score = request.POST['image_score']

    print(image_id)

    row_result = FacesNew.objects.all().get(id=image_id)

    row_result.score = image_score
    row_result.save()

    data = {
        'output': True
    }

    return JsonResponse(data)

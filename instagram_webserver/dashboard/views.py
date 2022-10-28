from django.shortcuts import render
from django.http import JsonResponse
from django.views import generic
from django.urls import reverse

from .models import FacesNew


# Create your views here.


class IndexView(generic.ListView):
    model = FacesNew
    template_name = 'dashboard/index.html'
    
    """
    login_url = '/accounts/login/'
    redirect_field_name = 'redirect_to'"""


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
           
            'review_array': 'cool'
        })


        return context

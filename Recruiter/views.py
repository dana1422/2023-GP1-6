from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse

def Recruiter(request):
    return render(request, 'Recruiter/RecruiterHome.html')
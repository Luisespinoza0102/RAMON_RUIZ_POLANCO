from django.shortcuts import render

def error_500_custom(request):
    return render(request, '500.html', status=500)
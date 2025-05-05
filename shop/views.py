from django.shortcuts import render

def index(request):
    return render(request, 'products/index.html')

def headsets(request):
    return render(request, 'products/headsets.html')

def keyboard(request):
    return render(request, 'products/keyboard.html')

def mouse(request):
    return render(request, 'products/mouse.html')



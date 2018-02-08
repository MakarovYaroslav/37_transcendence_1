from django.shortcuts import render


def index(request):
    return render(request, 'transcendence/index.html')


def user_info(request, user_id):
    return render(request,
                  'transcendence/user_info.html',
                  {'user_id': user_id})

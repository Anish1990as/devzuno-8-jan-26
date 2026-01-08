from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required(login_url='/client/login/')
def create_order(request):
    return render(request, 'billing/create_order.html')

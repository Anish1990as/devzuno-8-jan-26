
from django.shortcuts import render
def new_ticket(request):
    return render(request, 'support/new_ticket.html')

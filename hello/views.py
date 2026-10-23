from django.shortcuts import render, redirect
from .entities.user import User
from .entities.work_order import Work_order
from .enums.work_order_status import Status
# Create your views here.

def work_orders(request):
    work_orders = Work_order.get_all()
    counters = Work_order.get_counters()
    return render(request, 'hello/work_orders.html', {'work_orders':work_orders,'counters':counters})


def people(request):
    users = User.get_all()
    return render(request, 'hello/people.html', {'users':users})

def index(request):
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if User.check_login(email, password):
            return redirect('work_orders')
    
    return render(request, 'hello/index.html')

def signup(request):
    
    if request.method == 'POST':
        name = request.POST.get('name')
        account = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm-password')
        
        if User.save(name, account, password, confirm_password):
           return redirect('index')
    
    return render(request, 'hello/signup.html')


def add_work_order(request):
    users = Work_order.get_responsibles()
    error = None

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()

        if not title or not description:
            error = 'Title and description are required.'
        elif len(title) > 60:
            error = 'Title must have at most 60 characters.'
        else:
            try:
                status = Status(int(request.POST.get('status', '')))
                responsible = int(request.POST.get('responsible', ''))
            except (ValueError, TypeError):
                error = 'Invalid status or responsible.'
            else:
                if not any(u['id'] == responsible for u in users):
                    error = 'Please select a valid responsible.'
                else:
                    Work_order.create(
                        title, description, status.value, responsible
                    )
                    return redirect('work_orders')

    return render(request, 'hello/add_work_order.html', {
    'users': users,
    'statuses': list(Status),
    'error': error
})

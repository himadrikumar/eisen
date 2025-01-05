from django.shortcuts import render, redirect, get_object_or_404
from .models import Category, Task
from .forms import TaskForm
from datetime import date, timedelta
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .forms import CustomUserChangeForm
from django.contrib.auth import logout

from datetime import datetime

def landing_page(request):
    return render(request, 'eisens/landing_page.html')


@login_required
def account_details(request):
    if request.method == 'POST':
        if 'save_changes' in request.POST:
            form = CustomUserChangeForm(request.POST, instance=request.user)
            if form.is_valid():
                form.save()
                return redirect('eisens:index')  # Redirect to avoid re-posting the form
        elif 'delete_account' in request.POST:
            user = request.user
            logout(request)  # Log out the user
            user.delete()  # Delete the user account
            return redirect('eisens:index')  # Redirect to home after account deletion
    else:
        form = CustomUserChangeForm(instance=request.user)

    return render(request, 'eisens/account_details.html', {'form': form})


@login_required
def index(request):
    # Get today's date
    today = date.today()
    tomorrow = today + timedelta(days=1)

    # Check if carry-forward logic has already been executed today
    carry_forward_done = request.session.get('carry_forward_done', '')

    if carry_forward_done != str(today):
        # Filter incomplete tasks from previous days belonging to the current user
        incomplete_tasks = Task.objects.filter(
            date_added__date__lt=today,  # Tasks added before today
            completed=False,             # Tasks that are incomplete
            owner=request.user           # Tasks owned by the current user
        )

        for task in incomplete_tasks:
            # Check if the task already exists for today to avoid duplication
            duplicate_exists = Task.objects.filter(
                text=task.text,
                category=task.category,
                date_added__date=today,  # Already created for today
                owner=request.user       # Owned by the same user
            ).exists()

            if not duplicate_exists:
                # Create the carried-forward task
                Task.objects.create(
                    category=task.category,
                    text=task.text,
                    date_added=today,  # Assign today's date
                    completed=False,   # Keep it incomplete
                    owner=request.user
                )

        # Mark carry-forward as done for today
        request.session['carry_forward_done'] = str(today)

    categories = Category.objects.prefetch_related('task_set').all()
    form = TaskForm() 

    # Get all unique task dates
    task_dates = Task.objects.filter(owner=request.user).dates('date_added', 'day', order='DESC')

    # Get the selected date from the request
    selected_date = request.GET.get('date')
    if selected_date:
        try:
            filter_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
        except ValueError:
            filter_date = datetime.now().date()
    else:
        filter_date = datetime.now().date()  # Default to today's tasks

    # Add filtered tasks as an attribute
    for category in categories:
        # Filter tasks by selected date, ensuring no duplicate logic
        category.filtered_tasks = category.task_set.filter(
            date_added__date=filter_date,
            owner=request.user
        ).distinct()


    # Handle adding, toggling, and editing tasks (same as before)
    if request.method == 'POST' and 'add_task' in request.POST:
        form = TaskForm(request.POST)
        if form.is_valid():
            new_topic = form.save(commit=False)
            new_topic.owner = request.user
            new_topic.save()
            return redirect('eisens:index')

    if request.method == 'POST' and 'toggle_complete' in request.POST:
        task_to_toggle = get_object_or_404(Task, id=request.POST['task_id'])
        task_to_toggle.completed = not task_to_toggle.completed
        task_to_toggle.save()
        return redirect('eisens:index')

    edit_task_id = request.GET.get('edit_task_id')
    edit_form = None
    if edit_task_id:
        task_to_edit = get_object_or_404(Task, id=edit_task_id)
        if request.method == 'POST' and 'edit_task' in request.POST:
            edit_form = TaskForm(request.POST, instance=task_to_edit)
            if edit_form.is_valid():
                edited_task = edit_form.save(commit=False)
    
                # Check if a similar task already exists for the same day
                if not Task.objects.filter(
                    text=edited_task.text,
                    category=edited_task.category,
                    owner=request.user,
                    date_added__date=edited_task.date_added.date(),
                    completed=edited_task.completed
                ).exists():
                    edited_task.save()  # Save only if no duplicates
                return redirect('eisens:index')
        else:
            edit_form = TaskForm(instance=task_to_edit)


    context = {
        'categories': categories,
        'form': form,
        'edit_form': edit_form,
        'edit_task_id': edit_task_id,
        'task_dates': task_dates,
        'filter_date': filter_date,
        'today': today,
    }
    return render(request, 'eisens/index.html', context)


@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.completed = True
    task.delete()  # Delete the task
    for i in Task.objects.all():
        if i.text == task.text and i.category == task.category and i.id == task.id:
            i.completed = True
            i.delete()
    return redirect('eisens:index')  # Redirect back to the index page

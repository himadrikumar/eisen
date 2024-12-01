from django.shortcuts import render, redirect, get_object_or_404
from .models import Category, Task
from .forms import TaskForm
from datetime import date, timedelta

from datetime import datetime

def index(request):
    today = date.today()
    tomorrow = today + timedelta(days=1)

    # Only carry forward tasks that haven't been carried forward yet
    incomplete_tasks = Task.objects.filter(date_added__date__lt=today, completed=False)

    for task in incomplete_tasks:
        # Check if a task with the same text already exists for today to avoid duplication
        if not Task.objects.filter(text=task.text, category=task.category, date_added__date=today).exists():
            # Create the carried forward task with updated date_added to today
            Task.objects.create(
                category=task.category,
                text=task.text,
                date_added=tomorrow  # Set the new date_added to tomorrow
            )

    categories = Category.objects.prefetch_related('task_set').all()
    form = TaskForm()

    # Get all unique task dates
    task_dates = Task.objects.dates('date_added', 'day', order='DESC')

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
        category.filtered_tasks = category.task_set.filter(date_added__date=filter_date)

    # Handle adding, toggling, and editing tasks (same as before)
    if request.method == 'POST' and 'add_task' in request.POST:
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
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
                edit_form.save()
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


def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.delete()  # Delete the task
    return redirect('eisens:index')  # Redirect back to the index page

#
# from django.shortcuts import render, redirect, get_object_or_404
# from .models import Page, Category, Task
# from .forms import TaskForm
# def index(request):
#     pages = Page.objects.all().order_by('-date_created')
#     current_page_id = request.GET.get('page_id', None)
#     current_page = None
#
#     if current_page_id:
#         current_page = get_object_or_404(Page, id=current_page_id)
#     else:
#         # Default to the most recent page
#         if pages.exists():
#             current_page = pages.first()
#
#     categories = current_page.categories.all() if current_page else []
#
#     form = TaskForm()
#     edit_task_id = request.GET.get('edit_task_id')
#     edit_form = None
#
#     if current_page and request.method == 'POST':
#         # Add task
#         if 'add_task' in request.POST:
#             form = TaskForm(request.POST)
#             if form.is_valid():
#                 new_task = form.save(commit=False)  # Create but don't save
#                 # Here, specify the category
#                 category_id = request.POST.get('category_id')
#                 category = get_object_or_404(Category, id=category_id, page=current_page)
#                 new_task.category = category
#                 new_task.save()
#                 return redirect(f'?page_id={current_page.id}')
#
#         # Edit task
#         elif 'edit_task' in request.POST and edit_task_id:
#             task_to_edit = get_object_or_404(Task, id=edit_task_id)
#             edit_form = TaskForm(request.POST, instance=task_to_edit)
#             if edit_form.is_valid():
#                 edit_form.save()
#                 return redirect('eisens:index') + f'?page_id={current_page.id}'
#
#     # Pre-fill edit form for GET requests
#     if edit_task_id:
#         task_to_edit = get_object_or_404(Task, id=edit_task_id)
#         edit_form = TaskForm(instance=task_to_edit)
#
#     context = {
#         'pages': pages,
#         'current_page': current_page,
#         'categories': categories,
#         'form': form,
#         'edit_form': edit_form,
#         'edit_task_id': edit_task_id,
#         'current_page_id': current_page.id if current_page else None,
#     }
#     return render(request, 'eisens/index.html', context)
#
# def new_page(request):
#     new_page = Page.objects.create()  # Assuming Page has no required fields
#     return redirect('eisens:index') + f'?page_id={new_page.id}'

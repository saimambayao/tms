from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from datetime import datetime, timedelta
import csv

from .models import Staff, StaffTeam, StaffAttendance, StaffPerformance, Task, TaskCategory, TaskComment, TaskTimeLog


class StaffListView(LoginRequiredMixin, ListView):
    """List all staff members with filtering and search capabilities."""
    model = Staff
    template_name = 'staff/staff_list.html'
    context_object_name = 'staff_members'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Staff.objects.filter(is_active=True)
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(full_name__icontains=search_query) |
                Q(position__icontains=search_query) |
                Q(email__icontains=search_query)
            )
        
        # Filter by division
        division = self.request.GET.get('division')
        if division:
            queryset = queryset.filter(division=division)
        
        # Filter by employment status
        status = self.request.GET.get('employment_status')
        if status:
            queryset = queryset.filter(employment_status=status)
        
        # Filter by office
        office = self.request.GET.get('office')
        if office:
            queryset = queryset.filter(office=office)
        
        return queryset.order_by('full_name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['divisions'] = Staff.DIVISION_CHOICES
        context['employment_statuses'] = Staff.EMPLOYMENT_STATUS_CHOICES
        context['offices'] = Staff.OFFICE_CHOICES
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_division'] = self.request.GET.get('division', '')
        context['selected_status'] = self.request.GET.get('employment_status', '')
        context['selected_office'] = self.request.GET.get('office', '')
        return context


class StaffDetailView(LoginRequiredMixin, DetailView):
    """Display detailed information about a staff member."""
    model = Staff
    template_name = 'staff/staff_detail.html'
    context_object_name = 'staff_member'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        staff = self.get_object()
        
        # Get recent attendance records
        context['recent_attendance'] = staff.attendance_records.filter(
            date__gte=timezone.now().date() - timedelta(days=30)
        ).order_by('-date')[:10]
        
        # Get recent performance evaluations
        context['recent_evaluations'] = staff.performance_records.order_by('-evaluation_date')[:5]
        
        # Get teams this staff is part of
        context['teams'] = staff.teams.filter(is_active=True)
        
        # Get staff they supervise
        context['supervised_staff'] = Staff.objects.filter(
            supervisors__supervisor=staff
        )
        
        # Get their supervisors
        context['supervisors'] = Staff.objects.filter(
            supervised_staff__staff=staff
        )
        
        return context


@login_required
def staff_dashboard(request):
    """Staff management dashboard with overview statistics and task management."""
    # Get overall statistics
    total_staff = Staff.objects.filter(is_active=True).count()
    
    # Count by division
    division_stats = Staff.objects.filter(is_active=True).values('division').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Add percentage calculations
    for stat in division_stats:
        stat['percentage'] = round((stat['count'] / total_staff * 100), 1) if total_staff > 0 else 0
    
    # Count by employment status
    status_stats = Staff.objects.filter(is_active=True).values('employment_status').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Add percentage calculations
    for stat in status_stats:
        stat['percentage'] = round((stat['count'] / total_staff * 100), 1) if total_staff > 0 else 0
    
    # Recent hires (last 30 days)
    recent_hires = Staff.objects.filter(
        is_active=True,
        date_hired__gte=timezone.now().date() - timedelta(days=30)
    ).order_by('-date_hired')
    
    # Attendance summary for today
    today = timezone.now().date()
    attendance_today = StaffAttendance.objects.filter(date=today)
    attendance_summary = {
        'present': attendance_today.filter(status='present').count(),
        'absent': attendance_today.filter(status='absent').count(),
        'late': attendance_today.filter(status='late').count(),
        'on_leave': attendance_today.filter(
            status__in=['sick_leave', 'vacation_leave']
        ).count(),
    }
    
    # Teams overview
    active_teams = StaffTeam.objects.filter(is_active=True).count()
    
    # Task statistics
    all_tasks = Task.objects.all()
    task_stats = {
        'total_tasks': all_tasks.count(),
        'pending_tasks': all_tasks.filter(status='pending').count(),
        'in_progress_tasks': all_tasks.filter(status='in_progress').count(),
        'completed_tasks': all_tasks.filter(status='completed').count(),
        'overdue_tasks': all_tasks.filter(
            due_date__lt=timezone.now(),
            status__in=['pending', 'in_progress']
        ).count(),
    }
    
    # Recent tasks (last 7 days)
    recent_tasks = Task.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=7)
    ).select_related('assigned_to', 'category').order_by('-created_at')[:10]
    
    # High priority tasks
    urgent_tasks = Task.objects.filter(
        priority__in=['high', 'urgent'],
        status__in=['pending', 'in_progress']
    ).select_related('assigned_to', 'category').order_by('due_date')[:5]
    
    # Current user's profile and tasks (if they are staff)
    current_staff = None
    my_tasks = []
    try:
        current_staff = Staff.objects.get(user=request.user)
        my_tasks = Task.objects.filter(
            assigned_to=current_staff,
            status__in=['pending', 'in_progress']
        ).order_by('due_date')[:5]
    except Staff.DoesNotExist:
        pass
    
    context = {
        'total_staff': total_staff,
        'division_stats': division_stats,
        'status_stats': status_stats,
        'recent_hires': recent_hires,
        'attendance_summary': attendance_summary,
        'active_teams': active_teams,
        'task_stats': task_stats,
        'recent_tasks': recent_tasks,
        'urgent_tasks': urgent_tasks,
        'current_staff': current_staff,
        'my_tasks': my_tasks,
    }
    
    return render(request, 'staff/dashboard.html', context)


class StaffTeamListView(LoginRequiredMixin, ListView):
    """List all staff teams."""
    model = StaffTeam
    template_name = 'staff/team_list.html'
    context_object_name = 'teams'
    
    def get_queryset(self):
        return StaffTeam.objects.filter(is_active=True).annotate(
            member_count=Count('members')
        ).order_by('name')


class StaffTeamDetailView(LoginRequiredMixin, DetailView):
    """Display detailed information about a staff team."""
    model = StaffTeam
    template_name = 'staff/team_detail.html'
    context_object_name = 'team'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        team = self.get_object()
        
        # Get team members with their recent performance
        members = team.members.filter(is_active=True).prefetch_related('performance_records')
        context['members'] = members
        
        return context


@login_required
def attendance_tracking(request):
    """Attendance tracking interface."""
    today = timezone.now().date()
    
    if request.method == 'POST':
        staff_id = request.POST.get('staff_id')
        status = request.POST.get('status')
        time_in = request.POST.get('time_in')
        time_out = request.POST.get('time_out')
        notes = request.POST.get('notes', '')
        
        try:
            staff = Staff.objects.get(id=staff_id)
            
            # Create or update attendance record
            attendance, created = StaffAttendance.objects.get_or_create(
                staff=staff,
                date=today,
                defaults={
                    'status': status,
                    'time_in': datetime.strptime(time_in, '%H:%M').time() if time_in else None,
                    'time_out': datetime.strptime(time_out, '%H:%M').time() if time_out else None,
                    'notes': notes
                }
            )
            
            if not created:
                attendance.status = status
                if time_in:
                    attendance.time_in = datetime.strptime(time_in, '%H:%M').time()
                if time_out:
                    attendance.time_out = datetime.strptime(time_out, '%H:%M').time()
                attendance.notes = notes
                attendance.save()
            
            messages.success(request, f"Attendance recorded for {staff.full_name}")
            
        except Staff.DoesNotExist:
            messages.error(request, "Staff member not found")
        except ValueError as e:
            messages.error(request, f"Invalid time format: {str(e)}")
    
    # Get today's attendance
    todays_attendance = StaffAttendance.objects.filter(date=today).select_related('staff')
    
    # Get staff who haven't marked attendance
    staff_with_attendance = todays_attendance.values_list('staff_id', flat=True)
    staff_without_attendance = Staff.objects.filter(
        is_active=True
    ).exclude(id__in=staff_with_attendance)
    
    context = {
        'todays_attendance': todays_attendance,
        'staff_without_attendance': staff_without_attendance,
        'today': today,
    }
    
    return render(request, 'staff/attendance_tracking.html', context)




@login_required
def export_staff_csv(request):
    """Export staff data to CSV."""
    # Check if user has permission to export staff data
    if not (request.user.user_type == 'mp' or request.user.is_superuser):
        messages.error(request, "You don't have permission to export staff data.")
        return redirect('staff:staff_list')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="staff_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Full Name', 'Position', 'Division', 'Employment Status', 
        'Office', 'Email', 'Phone', 'Date Hired', 'Is Active'
    ])
    
    for staff in Staff.objects.all():
        writer.writerow([
            staff.full_name,
            staff.position,
            staff.get_division_display(),
            staff.get_employment_status_display(),
            staff.get_office_display(),
            staff.email,
            staff.phone_number,
            staff.date_hired,
            staff.is_active
        ])
    
    return response


@login_required
def staff_performance_overview(request):
    """Overview of staff performance metrics."""
    # Get performance statistics
    recent_evaluations = StaffPerformance.objects.filter(
        evaluation_date__gte=timezone.now().date() - timedelta(days=365)
    )
    
    # Average ratings by division
    division_performance = recent_evaluations.values(
        'staff__division'
    ).annotate(
        avg_rating=Avg('overall_rating'),
        count=Count('id')
    ).order_by('-avg_rating')
    
    # Recent evaluations
    latest_evaluations = recent_evaluations.select_related(
        'staff', 'evaluated_by'
    ).order_by('-evaluation_date')[:10]
    
    # Performance distribution
    rating_distribution = recent_evaluations.values('overall_rating').annotate(
        count=Count('id')
    ).order_by('overall_rating')
    
    context = {
        'division_performance': division_performance,
        'latest_evaluations': latest_evaluations,
        'rating_distribution': rating_distribution,
        'total_evaluations': recent_evaluations.count(),
    }
    
    return render(request, 'staff/performance_overview.html', context)


@login_required
def attendance_report(request):
    """Generate attendance reports."""
    # Get date range from request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if not start_date or not end_date:
        # Default to current month
        today = timezone.now().date()
        start_date = today.replace(day=1)
        end_date = today
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Get attendance data
    attendance_records = StaffAttendance.objects.filter(
        date__range=[start_date, end_date]
    ).select_related('staff')
    
    # Aggregate by staff
    staff_attendance = {}
    for record in attendance_records:
        staff_id = record.staff.id
        if staff_id not in staff_attendance:
            staff_attendance[staff_id] = {
                'staff': record.staff,
                'present': 0,
                'absent': 0,
                'late': 0,
                'on_leave': 0,
                'total_hours': 0
            }
        
        if record.status == 'present':
            staff_attendance[staff_id]['present'] += 1
        elif record.status == 'absent':
            staff_attendance[staff_id]['absent'] += 1
        elif record.status == 'late':
            staff_attendance[staff_id]['late'] += 1
        elif record.status in ['sick_leave', 'vacation_leave']:
            staff_attendance[staff_id]['on_leave'] += 1
        
        staff_attendance[staff_id]['total_hours'] += record.hours_worked
    
    context = {
        'staff_attendance': staff_attendance.values(),
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'staff/attendance_report.html', context)


@login_required
def staff_profile(request):
    """Display the logged-in staff member's profile."""
    try:
        # Get the staff profile for the current user
        staff = Staff.objects.get(user=request.user)
    except Staff.DoesNotExist:
        messages.error(request, "Staff profile not found. Please contact system administrators.")
        return redirect('staff:dashboard')
    
    # Get supervisor information
    supervisor = None
    if hasattr(staff, 'supervisor_relationships'):
        supervisor_rel = staff.supervisor_relationships.first()
        if supervisor_rel:
            supervisor = supervisor_rel.supervisor
    
    # Get team members if this staff is a supervisor
    supervised_staff = []
    if hasattr(staff, 'supervised_staff'):
        supervised_staff = staff.supervised_staff.all()
    
    # Get recent attendance
    recent_attendance = StaffAttendance.objects.filter(
        staff=staff
    ).order_by('-date')[:10]
    
    # Get recent performance evaluations
    recent_evaluations = StaffPerformance.objects.filter(
        staff=staff
    ).order_by('-evaluation_date')[:5]
    
    context = {
        'staff': staff,
        'supervisor': supervisor,
        'supervised_staff': supervised_staff,
        'recent_attendance': recent_attendance,
        'recent_evaluations': recent_evaluations,
        'is_developer': request.user.is_superuser,
        'user_permissions': request.user.get_all_permissions(),
    }
    
    return render(request, 'staff/profile.html', context)


@login_required 
def edit_staff_profile(request):
    """Allow staff to edit their own profile (limited fields)."""
    try:
        staff = Staff.objects.get(user=request.user)
    except Staff.DoesNotExist:
        messages.error(request, "Staff profile not found.")
        return redirect('staff:dashboard')
    
    if request.method == 'POST':
        # Allow editing of limited fields
        email = request.POST.get('email', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        address = request.POST.get('address', '').strip()
        bio = request.POST.get('bio', '').strip()
        
        # Update staff profile
        if email:
            staff.email = email
            # Also update user email if different
            if staff.user and staff.user.email != email:
                staff.user.email = email
                staff.user.save()
        
        if phone_number:
            staff.phone_number = phone_number
        
        if address:
            staff.address = address
            
        if bio:
            staff.bio = bio
        
        staff.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('staff:profile')
    
    context = {
        'staff': staff,
    }
    
    return render(request, 'staff/edit_profile.html', context)


@login_required
def staff_directory(request):
    """Staff directory for internal use."""
    # Get all active staff
    staff_members = Staff.objects.filter(is_active=True).select_related('user')
    
    # Filter by division if requested
    division = request.GET.get('division')
    if division:
        staff_members = staff_members.filter(division=division)
    
    # Filter by office if requested  
    office = request.GET.get('office')
    if office:
        staff_members = staff_members.filter(office=office)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        staff_members = staff_members.filter(
            Q(full_name__icontains=search_query) |
            Q(position__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    # Group by division for better organization
    divisions = {}
    for staff in staff_members.order_by('division', 'full_name'):
        division_name = staff.get_division_display() or 'Other'
        if division_name not in divisions:
            divisions[division_name] = []
        divisions[division_name].append(staff)
    
    # Get available filter options
    division_choices = Staff.DIVISION_CHOICES
    office_choices = Staff.OFFICE_CHOICES
    
    context = {
        'divisions': divisions,
        'division_choices': division_choices,
        'office_choices': office_choices,
        'current_division': division,
        'current_office': office,
        'search_query': search_query,
        'total_staff': staff_members.count(),
    }
    
    return render(request, 'staff/directory.html', context)


# Task Management Views

@login_required
def task_list(request):
    """List all tasks with filtering capabilities."""
    tasks = Task.objects.select_related('assigned_to', 'assigned_by', 'category')
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        tasks = tasks.filter(status=status)
    
    # Filter by priority
    priority = request.GET.get('priority')
    if priority:
        tasks = tasks.filter(priority=priority)
    
    # Filter by assigned staff
    assigned_to = request.GET.get('assigned_to')
    if assigned_to:
        tasks = tasks.filter(assigned_to_id=assigned_to)
    
    # Filter by category
    category = request.GET.get('category')
    if category:
        tasks = tasks.filter(category_id=category)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        tasks = tasks.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(assigned_to__full_name__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(tasks.order_by('-created_at'), 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get filter options
    staff_choices = Staff.objects.filter(is_active=True).order_by('full_name')
    category_choices = TaskCategory.objects.filter(is_active=True).order_by('name')
    
    context = {
        'page_obj': page_obj,
        'tasks': page_obj.object_list,
        'staff_choices': staff_choices,
        'category_choices': category_choices,
        'status_choices': Task.STATUS_CHOICES,
        'priority_choices': Task.PRIORITY_CHOICES,
        'current_filters': {
            'status': status,
            'priority': priority,
            'assigned_to': assigned_to,
            'category': category,
            'search': search_query,
        }
    }
    
    return render(request, 'staff/task_list.html', context)


@login_required
def task_detail(request, task_id):
    """View task details with comments and time logs."""
    task = get_object_or_404(Task, id=task_id)
    
    # Get comments
    comments = task.comments.select_related('author').order_by('-created_at')
    
    # Get time logs
    time_logs = task.time_logs.select_related('staff').order_by('-start_time')
    
    # Handle comment creation
    if request.method == 'POST':
        comment_text = request.POST.get('comment')
        if comment_text:
            try:
                current_staff = Staff.objects.get(user=request.user)
                TaskComment.objects.create(
                    task=task,
                    author=current_staff,
                    comment=comment_text
                )
                messages.success(request, "Comment added successfully!")
            except Staff.DoesNotExist:
                messages.error(request, "Staff profile not found.")
        
        return redirect('staff:task_detail', task_id=task.id)
    
    context = {
        'task': task,
        'comments': comments,
        'time_logs': time_logs,
    }
    
    return render(request, 'staff/task_detail.html', context)


@login_required
def task_create(request):
    """Create a new task."""
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        assigned_to_id = request.POST.get('assigned_to')
        category_id = request.POST.get('category')
        priority = request.POST.get('priority', 'medium')
        due_date_str = request.POST.get('due_date')
        estimated_hours = request.POST.get('estimated_hours')
        
        try:
            assigned_to = Staff.objects.get(id=assigned_to_id)
            current_staff = Staff.objects.get(user=request.user)
            
            # Parse due date
            due_date = None
            if due_date_str:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M')
            
            # Create task
            task = Task.objects.create(
                title=title,
                description=description,
                assigned_to=assigned_to,
                assigned_by=current_staff,
                priority=priority,
                due_date=due_date,
                estimated_hours=float(estimated_hours) if estimated_hours else None
            )
            
            # Set category if provided
            if category_id:
                category = TaskCategory.objects.get(id=category_id)
                task.category = category
                task.save()
            
            messages.success(request, f"Task '{task.title}' created successfully!")
            return redirect('staff:task_detail', task_id=task.id)
            
        except Staff.DoesNotExist:
            messages.error(request, "Staff member not found.")
        except TaskCategory.DoesNotExist:
            messages.error(request, "Category not found.")
        except ValueError as e:
            messages.error(request, f"Invalid input: {str(e)}")
    
    # Get choices for form
    staff_choices = Staff.objects.filter(is_active=True).order_by('full_name')
    category_choices = TaskCategory.objects.filter(is_active=True).order_by('name')
    
    context = {
        'staff_choices': staff_choices,
        'category_choices': category_choices,
        'priority_choices': Task.PRIORITY_CHOICES,
    }
    
    return render(request, 'staff/task_create.html', context)


@login_required
def task_update_status(request, task_id):
    """Update task status via AJAX."""
    if request.method == 'POST':
        task = get_object_or_404(Task, id=task_id)
        new_status = request.POST.get('status')
        progress = request.POST.get('progress')
        
        if new_status in dict(Task.STATUS_CHOICES):
            task.status = new_status
            
            if progress:
                task.progress_percentage = int(progress)
            
            if new_status == 'completed':
                task.mark_completed()
            
            task.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Task status updated to {task.get_status_display()}'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


@login_required
def my_tasks(request):
    """Show tasks assigned to the current user."""
    try:
        current_staff = Staff.objects.get(user=request.user)
    except Staff.DoesNotExist:
        messages.error(request, "Staff profile not found.")
        return redirect('staff:dashboard')
    
    # Get user's tasks
    tasks = Task.objects.filter(assigned_to=current_staff).select_related('category')
    
    # Filter by status
    status = request.GET.get('status', 'active')  # Default to active tasks
    if status == 'active':
        tasks = tasks.filter(status__in=['pending', 'in_progress'])
    elif status == 'completed':
        tasks = tasks.filter(status='completed')
    elif status == 'all':
        pass  # Show all tasks
    else:
        tasks = tasks.filter(status=status)
    
    # Sort by priority and due date
    tasks = tasks.order_by('-priority', 'due_date')
    
    # Task statistics for current user
    user_task_stats = {
        'total': Task.objects.filter(assigned_to=current_staff).count(),
        'pending': Task.objects.filter(assigned_to=current_staff, status='pending').count(),
        'in_progress': Task.objects.filter(assigned_to=current_staff, status='in_progress').count(),
        'completed': Task.objects.filter(assigned_to=current_staff, status='completed').count(),
        'overdue': Task.objects.filter(
            assigned_to=current_staff,
            due_date__lt=timezone.now(),
            status__in=['pending', 'in_progress']
        ).count(),
    }
    
    context = {
        'my_tasks': tasks,
        'current_staff': current_staff,
        'my_task_stats': user_task_stats,
        'current_status_filter': status,
        'status_choices': Task.STATUS_CHOICES,
    }
    
    return render(request, 'staff/my_tasks.html', context)
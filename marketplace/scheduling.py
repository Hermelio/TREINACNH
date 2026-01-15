"""
Utility functions for scheduling and availability management.
"""
from datetime import datetime, timedelta, date, time
from django.db.models import Q
from .models import InstructorAvailability, Appointment


def get_available_time_slots(instructor, target_date, duration_hours=1.0):
    """
    Get available time slots for an instructor on a specific date.
    
    Args:
        instructor: InstructorProfile instance
        target_date: date object
        duration_hours: float, duration of the lesson (default 1.0 hour)
    
    Returns:
        List of tuples (start_time, end_time) representing available slots
    """
    # Get weekday (0=Monday, 6=Sunday)
    weekday = target_date.weekday()
    
    # Get instructor's availability for this weekday
    availabilities = InstructorAvailability.objects.filter(
        instructor=instructor,
        weekday=weekday,
        is_active=True
    ).order_by('start_time')
    
    if not availabilities.exists():
        return []
    
    # Get existing appointments for this date (not cancelled)
    appointments = Appointment.objects.filter(
        instructor=instructor,
        appointment_date=target_date,
        is_cancelled=False
    ).order_by('start_time')
    
    available_slots = []
    
    # For each availability window
    for availability in availabilities:
        current_time = availability.start_time
        end_time = availability.end_time
        
        # Generate slots in this window
        while True:
            # Calculate end of this slot
            slot_end = (datetime.combine(date.today(), current_time) + 
                       timedelta(hours=duration_hours)).time()
            
            # Check if slot fits in availability window
            if slot_end > end_time:
                break
            
            # Check if slot conflicts with any appointment
            is_available = True
            for appt in appointments:
                # Check overlap
                if (current_time < appt.end_time and slot_end > appt.start_time):
                    is_available = False
                    # Jump to end of this appointment
                    current_time = appt.end_time
                    break
            
            if is_available:
                available_slots.append((current_time, slot_end))
                # Move to next slot (30 minute increments)
                current_time = (datetime.combine(date.today(), current_time) + 
                               timedelta(minutes=30)).time()
            
            # Prevent infinite loop
            if current_time >= end_time:
                break
    
    return available_slots


def format_time_slot(start_time, end_time):
    """Format time slot for display"""
    return f"{start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}"


def get_next_available_dates(instructor, days_ahead=30, max_results=10):
    """
    Get next available dates for an instructor.
    
    Args:
        instructor: InstructorProfile instance
        days_ahead: int, number of days to look ahead
        max_results: int, maximum number of dates to return
    
    Returns:
        List of date objects that have availability
    """
    today = date.today()
    available_dates = []
    
    for i in range(days_ahead):
        check_date = today + timedelta(days=i)
        slots = get_available_time_slots(instructor, check_date)
        
        if slots:
            available_dates.append(check_date)
            
            if len(available_dates) >= max_results:
                break
    
    return available_dates


def calculate_duration(start_time, end_time):
    """Calculate duration in hours between two times"""
    start = datetime.combine(date.today(), start_time)
    end = datetime.combine(date.today(), end_time)
    duration = (end - start).total_seconds() / 3600
    return round(duration, 1)


def create_appointment_from_lead(lead, appointment_date, start_time, end_time):
    """
    Create an appointment from a lead.
    
    Args:
        lead: Lead instance
        appointment_date: date object
        start_time: time object
        end_time: time object
    
    Returns:
        Appointment instance or None if conflict
    """
    from .models import Appointment, LeadStatusChoices
    
    # Calculate duration
    duration = calculate_duration(start_time, end_time)
    
    # Create appointment
    appointment = Appointment(
        lead=lead,
        instructor=lead.instructor,
        student_user=lead.student_user,
        appointment_date=appointment_date,
        start_time=start_time,
        end_time=end_time,
        duration_hours=duration
    )
    
    # Validate (checks for conflicts)
    try:
        appointment.clean()
        appointment.save()
        
        # Update lead status to SCHEDULED
        lead.status = LeadStatusChoices.SCHEDULED
        lead.save()
        
        return appointment
    except Exception as e:
        print(f"Error creating appointment: {e}")
        return None

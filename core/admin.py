from django.contrib import admin
import csv
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Q
from django.contrib.admin import SimpleListFilter

# Register your models here.
from core.models import WorkShop, WorkshopRegistration


class WorkshopStatusFilter(SimpleListFilter):
    title = 'Workshop Status'
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return (
            ('upcoming', 'Upcoming Workshops'),
            ('ongoing', 'Ongoing Workshops'),
            ('completed', 'Completed Workshops'),
        )

    def queryset(self, request, queryset):
        today = timezone.now().date()
        if self.value() == 'upcoming':
            return queryset.filter(workshop_date__gt=today, is_ended=False)
        elif self.value() == 'ongoing':
            return queryset.filter(workshop_date=today, is_ended=False)
        elif self.value() == 'completed':
            return queryset.filter(Q(workshop_date__lt=today) | Q(is_ended=True))


class AttendanceFilter(SimpleListFilter):
    title = 'Attendance Type'
    parameter_name = 'attendance'

    def lookups(self, request, model_admin):
        return (
            ('physical', 'Physical Attendance'),
            ('virtual', 'Virtual Attendance'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'physical':
            return queryset.filter(will_attend_physical=True)
        elif self.value() == 'virtual':
            return queryset.filter(will_attend_physical=False)


@admin.register(WorkShop)
class WorkShopAdmin(admin.ModelAdmin):
    list_display = (
        'workshop_name', 
        'workshop_date', 
        'workshop_time',
        'workshop_location', 
        'is_ended', 
        'get_registrations_count',
        'get_physical_attendees',
        'get_virtual_attendees'
    )
    search_fields = ('workshop_name', 'workshop_location', 'workshop_description')
    list_filter = ('is_ended', WorkshopStatusFilter, 'workshop_date')
    date_hierarchy = 'workshop_date'
    readonly_fields = ('get_registrations_count',)
    
    fieldsets = (
        ('Workshop Information', {
            'fields': ('workshop_name', 'workshop_date', 'workshop_time', 'workshop_location', 'workshop_description')
        }),
        ('Media', {
            'fields': ('workshop_image_header',)
        }),
        ('Status', {
            'fields': ('is_ended',)
        }),
        ('Statistics', {
            'fields': ('get_registrations_count',),
            'classes': ('collapse',)
        }),
    )
    
    def get_registrations_count(self, obj):
        return obj.registrations.count()
    get_registrations_count.short_description = 'Total Registrations'
    
    def get_physical_attendees(self, obj):
        return obj.registrations.filter(will_attend_physical=True).count()
    get_physical_attendees.short_description = 'Physical'
    
    def get_virtual_attendees(self, obj):
        return obj.registrations.filter(will_attend_physical=False).count()
    get_virtual_attendees.short_description = 'Virtual'


@admin.register(WorkshopRegistration)
class WorkshopRegistrationAdmin(admin.ModelAdmin):
    list_display = (
        'user_name',
        'workshop',
        'user_email',
        'country',
        'registration_date',
        'will_attend_physical',
        'django_experience',
        'get_workshop_status'
    )
    search_fields = (
        'user_name',
        'user_email',
        'phone_number',
        'country',
        'workshop__workshop_name'
    )
    list_filter = (
        'workshop',
        'country',
        'will_attend_physical',
        'django_experience',
        AttendanceFilter,
        'registration_date'
    )
    ordering = ('-registration_date',)
    date_hierarchy = 'registration_date'
    
    fieldsets = (
        ('Participant Information', {
            'fields': ('user_name', 'user_email', 'phone_number', 'country')
        }),
        ('Workshop Details', {
            'fields': ('workshop', 'django_experience'),
            'description': (
                'Django experience is optional for non-Django events'
            )
        }),
        ('Attendance Preference', {
            'fields': ('will_attend_physical',)
        }),
        ('Registration Info', {
            'fields': ('registration_date',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('registration_date',)
    
    actions = ['export_as_csv', 'export_workshop_specific_csv']
    
    def get_workshop_status(self, obj):
        if obj.workshop.is_ended:
            return "Completed"
        elif obj.workshop.workshop_date < timezone.now().date():
            return "Past"
        elif obj.workshop.workshop_date == timezone.now().date():
            return "Today"
        else:
            return "Upcoming"
    get_workshop_status.short_description = 'Workshop Status'
    
    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = (
            'attachment; filename={}.csv'.format(
                meta.verbose_name_plural.replace(' ', '_').lower()
            )
        )
        writer = csv.writer(response)
        
        # Write header
        header = [
            'Name', 'Email', 'Phone', 'Country', 'Workshop',
            'Workshop Date', 'Location', 'Experience',
            'Physical Attendance', 'Registration Date'
        ]
        writer.writerow(header)
        
        # Write data rows
        for obj in queryset:
            row = [
                obj.user_name,
                obj.user_email,
                obj.phone_number or 'N/A',
                obj.country or 'N/A',
                obj.workshop.workshop_name,
                obj.workshop.workshop_date.strftime('%Y-%m-%d'),
                obj.workshop.workshop_location,
                obj.django_experience or 'N/A',
                'Yes' if obj.will_attend_physical else 'No',
                obj.registration_date.strftime('%Y-%m-%d %H:%M:%S')
            ]
            writer.writerow(row)
        
        return response
    
    export_as_csv.short_description = "Export selected registrations as CSV"
    
    def export_workshop_specific_csv(self, request, queryset):
        # Group by workshop for better organization
        workshops = {}
        for registration in queryset:
            workshop_name = registration.workshop.workshop_name
            if workshop_name not in workshops:
                workshops[workshop_name] = []
            workshops[workshop_name].append(registration)
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = (
            'attachment; filename=workshop_registrations_by_event.csv'
        )
        writer = csv.writer(response)
        
        for workshop_name, registrations in workshops.items():
            # Write workshop header
            writer.writerow([f"Workshop: {workshop_name}"])
            writer.writerow([
                'Name', 'Email', 'Phone', 'Country', 'Experience',
                'Physical Attendance', 'Registration Date'
            ])
            
            # Write registrations for this workshop
            for reg in registrations:
                row = [
                    reg.user_name,
                    reg.user_email,
                    reg.phone_number or 'N/A',
                    reg.country or 'N/A',
                    reg.django_experience or 'N/A',
                    'Yes' if reg.will_attend_physical else 'No',
                    reg.registration_date.strftime('%Y-%m-%d %H:%M:%S')
                ]
                writer.writerow(row)
            
            # Add empty row between workshops
            writer.writerow([])
        
        return response
    
    export_workshop_specific_csv.short_description = (
        "Export by workshop (grouped CSV)"
    )

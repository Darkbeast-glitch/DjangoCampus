from django.db import models

# Create your models here.


# a variable where you image will be stored

WORKSHOP_IMAGE_UPLOAD_PATH = 'header/workshop_images/'
    
# Model to add workshops
class WorkShop(models.Model):
    workshop_image_header = models.ImageField(upload_to=WORKSHOP_IMAGE_UPLOAD_PATH, null=True, blank=True, verbose_name="Workshop Image Header")
    workshop_name = models.CharField(max_length=255, verbose_name="Workshop Name", null=False, blank=False)
    workshop_date = models.DateField(verbose_name="Workshop Date", null=False, blank=False)
    workshop_time = models.TimeField(verbose_name="Workshop Time", null=True, blank=True)
    workshop_location = models.CharField(max_length=255, verbose_name="Workshop Location", null=False, blank=False)
    workshop_description = models.TextField(verbose_name="Workshop Description", null=True, blank=True)
    is_ended = models.BooleanField(default=False, verbose_name="Is Ended")
    
    
    class Meta:
        verbose_name = "Workshop"
        verbose_name_plural = "Workshops"
        ordering = ['-workshop_date', '-id']  
        # table_name = 'workshops'
        
    def __str__(self):
        return f"{self.workshop_name} - {self.workshop_date}"
    
    
    

#Experience in django

class DjangoExperience(models.TextChoices):
    BEGINNER = 'Beginner'
    INTERMEDIATE = 'Intermediate'
    ADVANCED = 'Advanced'

# Model to let users register for workshops
class WorkshopRegistration(models.Model):
    workshop = models.ForeignKey(
        WorkShop,
        on_delete=models.CASCADE,
        related_name='registrations',
        verbose_name="Workshop"
    )
    user_name = models.CharField(
        max_length=255,
        verbose_name="User Name",
        null=False,
        blank=False
    )
    user_email = models.EmailField(
        verbose_name="User Email",
        null=False,
        blank=False
    )
    phone_number = models.CharField(
        max_length=13,
        verbose_name="Phone Number",
        blank=True,
        null=True
    )
    country = models.CharField(
        max_length=100,
        verbose_name="Country",
        blank=True,
        null=True,
        help_text="Participant's country"
    )
    will_attend_physical = models.BooleanField(
        default=True,
        verbose_name="Will Attend Physically"
    )
    django_experience = models.CharField(
        max_length=20,
        choices=DjangoExperience.choices,
        blank=True,
        null=True,
        verbose_name="Django Experience Level",
        help_text="Optional: Only required for Django-specific workshops"
    )
    registration_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Registration Date"
    )
    
    class Meta:
        verbose_name = "Workshop Registration"
        verbose_name_plural = "Workshop Registrations"
        ordering = ['registration_date']
        unique_together = ['workshop', 'user_email']
        
    def __str__(self):
        return f"{self.user_name} registered for {self.workshop.workshop_name}"
    
    def get_attendance_display(self):
        """Return human-readable attendance type"""
        return "Physical" if self.will_attend_physical else "Virtual"
    
    def get_experience_display(self):
        """Return human-readable experience level"""
        return self.django_experience if self.django_experience else "N/A"

from rest_framework import serializers
from core.models import WorkShop, WorkshopRegistration
from drf_spectacular.utils import extend_schema_field


class WorkShopSerializer(serializers.ModelSerializer):
    """
    Serializer for WorkShop model.
    """
    registrations_count = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkShop
        fields = [
            'id', 'workshop_image_header', 'workshop_name', 'workshop_date','workshop_time', 'workshop_description', 'workshop_location',
            'is_ended', 'registrations_count'
        ]
        read_only_fields = ['id']
    
    @extend_schema_field(serializers.IntegerField)
    def get_registrations_count(self, obj):
        """Get the total number of registrations for this workshop."""
        return obj.registrations.count()


class WorkshopRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for WorkshopRegistration model.
    """
    workshop_name = serializers.CharField(
        source='workshop.workshop_name', read_only=True
    )
    workshop_date = serializers.DateField(
        source='workshop.workshop_date', read_only=True
    )
    workshop_time = serializers.TimeField(
        source='workshop.workshop_time', read_only=True
    )

    class Meta:
        model = WorkshopRegistration
        fields = [
            'id', 'workshop', 'workshop_name', 'workshop_date',
            'workshop_time', 'user_name', 'user_email', 'phone_number',
            'country', 'will_attend_physical', 'django_experience',
            'registration_date'
        ]
        read_only_fields = [
            'id', 'registration_date', 'workshop_name', 'workshop_date'
        ]
    
    def validate_user_email(self, value):
        """
        Validate that the email is properly formatted and not empty.
        """
        if not value or value.strip() == "":
            raise serializers.ValidationError("Email field cannot be empty.")
        return value.lower().strip()
    
    def validate_user_name(self, value):
        """
        Validate that the name is not empty and has reasonable length.
        """
        if not value or value.strip() == "":
            raise serializers.ValidationError("Name field cannot be empty.")
        if len(value.strip()) < 2:
            raise serializers.ValidationError(
                "Name must be at least 2 characters long."
            )
        return value.strip().title()


class WorkShopListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing workshops.
    """
    registrations_count = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkShop
        fields = [
            'id', 'workshop_image_header', 'workshop_name', 'workshop_date',
            'workshop_time', 'workshop_description', 'workshop_location',
            'is_ended', 'registrations_count'
        ]
        read_only_fields = ['id']
    
    @extend_schema_field(serializers.IntegerField)
    def get_registrations_count(self, obj):
        """Get the total number of registrations for this workshop."""
        return obj.registrations.count()

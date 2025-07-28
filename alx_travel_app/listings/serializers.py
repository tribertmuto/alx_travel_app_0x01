from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Listing, Booking


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model with basic information.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']
        read_only_fields = ['id']


class ListingSerializer(serializers.ModelSerializer):
    """
    Serializer for Listing model with full CRUD operations.
    """
    host = UserSerializer(read_only=True)
    host_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = Listing
        fields = [
            'id', 'title', 'description', 'location', 'property_type',
            'price_per_night', 'max_guests', 'bedrooms', 'bathrooms',
            'amenities', 'available', 'host', 'host_id', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'host']

    def validate_price_per_night(self, value):
        """
        Validate that price per night is positive.
        """
        if value <= 0:
            raise serializers.ValidationError("Price per night must be greater than zero.")
        return value

    def validate_max_guests(self, value):
        """
        Validate that max guests is positive.
        """
        if value <= 0:
            raise serializers.ValidationError("Maximum guests must be greater than zero.")
        return value

    def validate(self, data):
        """
        Cross-field validation for listing data.
        """
        # Validate bedrooms and bathrooms
        bedrooms = data.get('bedrooms', 0)
        bathrooms = data.get('bathrooms', 0)
        
        if bedrooms < 0:
            raise serializers.ValidationError("Number of bedrooms cannot be negative.")
        
        if bathrooms < 0:
            raise serializers.ValidationError("Number of bathrooms cannot be negative.")
        
        return data


class BookingSerializer(serializers.ModelSerializer):
    """
    Serializer for Booking model with validation and nested relationships.
    """
    guest = UserSerializer(read_only=True)
    guest_id = serializers.IntegerField(write_only=True, required=False)
    listing = ListingSerializer(read_only=True)
    listing_id = serializers.IntegerField(write_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    nights = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Booking
        fields = [
            'id', 'listing', 'listing_id', 'guest', 'guest_id',
            'check_in_date', 'check_out_date', 'number_of_guests',
            'total_price', 'nights', 'status', 'special_requests',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'guest', 'total_price', 'nights']

    def validate_number_of_guests(self, value):
        """
        Validate that number of guests is positive.
        """
        if value <= 0:
            raise serializers.ValidationError("Number of guests must be greater than zero.")
        return value

    def validate(self, data):
        """
        Cross-field validation for booking data.
        """
        check_in = data.get('check_in_date')
        check_out = data.get('check_out_date')
        listing_id = data.get('listing_id')
        number_of_guests = data.get('number_of_guests')
        
        # Validate check-in and check-out dates
        if check_in and check_out:
            if check_in >= check_out:
                raise serializers.ValidationError(
                    "Check-out date must be after check-in date."
                )
            
            # Calculate minimum stay (could be configurable)
            from datetime import timedelta
            min_stay = timedelta(days=1)
            if check_out - check_in < min_stay:
                raise serializers.ValidationError(
                    "Minimum stay is 1 night."
                )
        
        # Validate against listing capacity
        if listing_id and number_of_guests:
            try:
                listing = Listing.objects.get(id=listing_id)
                if number_of_guests > listing.max_guests:
                    raise serializers.ValidationError(
                        f"Number of guests ({number_of_guests}) exceeds listing capacity ({listing.max_guests})."
                    )
            except Listing.DoesNotExist:
                raise serializers.ValidationError("Invalid listing selected.")
        
        # Check for overlapping bookings
        if check_in and check_out and listing_id:
            from django.db.models import Q
            overlapping_bookings = Booking.objects.filter(
                listing_id=listing_id,
                status__in=['confirmed', 'pending']
            ).filter(
                Q(check_in_date__lt=check_out) & Q(check_out_date__gt=check_in)
            )
            
            # Exclude current booking if updating
            if self.instance:
                overlapping_bookings = overlapping_bookings.exclude(id=self.instance.id)
            
            if overlapping_bookings.exists():
                raise serializers.ValidationError(
                    "These dates are not available. Please choose different dates."
                )
        
        return data

    def create(self, validated_data):
        """
        Create a booking and calculate total price.
        """
        booking = super().create(validated_data)
        booking.calculate_total_price()
        return booking

    def update(self, instance, validated_data):
        """
        Update a booking and recalculate total price if dates changed.
        """
        old_check_in = instance.check_in_date
        old_check_out = instance.check_out_date
        
        booking = super().update(instance, validated_data)
        
        # Recalculate total price if dates changed
        if (booking.check_in_date != old_check_in or 
            booking.check_out_date != old_check_out):
            booking.calculate_total_price()
        
        return booking


class BookingCreateSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for booking creation with minimal fields.
    """
    class Meta:
        model = Booking
        fields = [
            'listing', 'check_in_date', 'check_out_date', 
            'number_of_guests', 'special_requests'
        ]

    def validate(self, data):
        """
        Simplified validation for booking creation.
        """
        check_in = data.get('check_in_date')
        check_out = data.get('check_out_date')
        
        if check_in and check_out:
            if check_in >= check_out:
                raise serializers.ValidationError(
                    "Check-out date must be after check-in date."
                )
        
        return data


class ListingDetailSerializer(ListingSerializer):
    """
    Extended serializer for listing detail view with additional information.
    """
    host = UserSerializer(read_only=True)
    recent_bookings_count = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    
    class Meta(ListingSerializer.Meta):
        fields = ListingSerializer.Meta.fields + [
            'recent_bookings_count', 'average_rating'
        ]
    
    def get_recent_bookings_count(self, obj):
        """
        Get count of recent bookings (last 30 days).
        """
        from datetime import datetime, timedelta
        thirty_days_ago = datetime.now().date() - timedelta(days=30)
        return obj.bookings.filter(
            created_at__date__gte=thirty_days_ago,
            status='confirmed'
        ).count()
    
    def get_average_rating(self, obj):
        """
        Calculate average rating for the listing.
        Note: This assumes you have a Rating model related to Listing.
        """
        # This would need to be implemented based on your rating system
        # For now, returning None as placeholder
        return None
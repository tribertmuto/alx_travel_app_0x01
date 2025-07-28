from rest_framework import serializers
from .models import Listing, Booking

class ListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = ['id', 'title', 'description', 'price', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class BookingSerializer(serializers.ModelSerializer):
    listing_title = serializers.CharField(source='listing.title', read_only=True)
    
    class Meta:
        model = Booking
        fields = ['id', 'listing', 'listing_title', 'user_name', 'booking_date', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

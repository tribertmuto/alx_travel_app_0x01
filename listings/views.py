from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Listing, Booking
from .serializers import ListingSerializer, BookingSerializer

class ListingViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing listing instances.
    
    Provides CRUD operations for listings:
    * list - GET /api/listings/
    * create - POST /api/listings/
    * retrieve - GET /api/listings/{id}/
    * update - PUT /api/listings/{id}/
    * partial_update - PATCH /api/listings/{id}/
    * destroy - DELETE /api/listings/{id}/
    """
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['price']
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'created_at', 'updated_at']
    ordering = ['-created_at']

class BookingViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing booking instances.
    
    Provides CRUD operations for bookings:
    * list - GET /api/bookings/
    * create - POST /api/bookings/
    * retrieve - GET /api/bookings/{id}/
    * update - PUT /api/bookings/{id}/
    * partial_update - PATCH /api/bookings/{id}/
    * destroy - DELETE /api/bookings/{id}/
    """
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['listing', 'booking_date']
    search_fields = ['user_name']
    ordering_fields = ['booking_date', 'created_at', 'updated_at']
    ordering = ['-created_at']

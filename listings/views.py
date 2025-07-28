from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models import Q
from .models import Listing, Booking
from .serializers import ListingSerializer, BookingSerializer


class ListingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing property listings.
    
    Provides CRUD operations for listings with filtering and search capabilities.
    """
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchBackend, filters.OrderingFilter]
    filterset_fields = ['location', 'property_type', 'price_per_night']
    search_fields = ['title', 'description', 'location']
    ordering_fields = ['created_at', 'price_per_night', 'rating']
    ordering = ['-created_at']

    def get_permissions(self):
        """
        Instantiate and return the list of permissions required for this view.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticatedOrReadOnly]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """
        Save the listing with the current user as the host.
        """
        serializer.save(host=self.request.user)

    @swagger_auto_schema(
        method='get',
        operation_description="Get available listings within a date range",
        manual_parameters=[
            openapi.Parameter(
                'check_in',
                openapi.IN_QUERY,
                description="Check-in date (YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE
            ),
            openapi.Parameter(
                'check_out',
                openapi.IN_QUERY,
                description="Check-out date (YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE
            ),
        ]
    )
    @action(detail=False, methods=['get'])
    def available(self, request):
        """
        Get listings available for booking within a specified date range.
        """
        check_in = request.query_params.get('check_in')
        check_out = request.query_params.get('check_out')
        
        if not check_in or not check_out:
            return Response(
                {'error': 'Both check_in and check_out dates are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Filter out listings that have bookings overlapping with the requested dates
        overlapping_bookings = Booking.objects.filter(
            Q(check_in_date__lte=check_out) & Q(check_out_date__gte=check_in),
            status__in=['confirmed', 'pending']
        ).values_list('listing_id', flat=True)
        
        available_listings = self.queryset.exclude(id__in=overlapping_bookings)
        
        page = self.paginate_queryset(available_listings)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(available_listings, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        method='get',
        operation_description="Get listings by location"
    )
    @action(detail=False, methods=['get'])
    def by_location(self, request):
        """
        Get listings filtered by location.
        """
        location = request.query_params.get('location')
        if not location:
            return Response(
                {'error': 'Location parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        listings = self.queryset.filter(location__icontains=location)
        
        page = self.paginate_queryset(listings)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(listings, many=True)
        return Response(serializer.data)


class BookingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing bookings.
    
    Provides CRUD operations for bookings with user-specific filtering.
    """
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'listing']
    ordering_fields = ['created_at', 'check_in_date', 'total_price']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Filter bookings based on user role:
        - Regular users see only their own bookings
        - Staff users see all bookings
        """
        if self.request.user.is_staff:
            return Booking.objects.all()
        return Booking.objects.filter(guest=self.request.user)

    def perform_create(self, serializer):
        """
        Save the booking with the current user as the guest.
        """
        serializer.save(guest=self.request.user)

    @swagger_auto_schema(
        method='post',
        operation_description="Cancel a booking",
        responses={200: "Booking cancelled successfully"}
    )
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Cancel a specific booking.
        """
        booking = self.get_object()
        
        # Check if the user has permission to cancel this booking
        if booking.guest != request.user and not request.user.is_staff:
            return Response(
                {'error': 'You do not have permission to cancel this booking'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if booking can be cancelled
        if booking.status == 'cancelled':
            return Response(
                {'error': 'Booking is already cancelled'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if booking.status == 'completed':
            return Response(
                {'error': 'Cannot cancel a completed booking'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        booking.status = 'cancelled'
        booking.save()
        
        serializer = self.get_serializer(booking)
        return Response({
            'message': 'Booking cancelled successfully',
            'booking': serializer.data
        })

    @swagger_auto_schema(
        method='post',
        operation_description="Confirm a pending booking",
        responses={200: "Booking confirmed successfully"}
    )
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """
        Confirm a pending booking (host only).
        """
        booking = self.get_object()
        
        # Check if the user is the host of the listing
        if booking.listing.host != request.user:
            return Response(
                {'error': 'Only the listing host can confirm bookings'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if booking.status != 'pending':
            return Response(
                {'error': 'Only pending bookings can be confirmed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        booking.status = 'confirmed'
        booking.save()
        
        serializer = self.get_serializer(booking)
        return Response({
            'message': 'Booking confirmed successfully',
            'booking': serializer.data
        })

    @swagger_auto_schema(
        method='get',
        operation_description="Get user's booking history"
    )
    @action(detail=False, methods=['get'])
    def my_bookings(self, request):
        """
        Get all bookings for the current user.
        """
        bookings = Booking.objects.filter(guest=request.user)
        
        page = self.paginate_queryset(bookings)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(bookings, many=True)
        return Response(serializer.data)
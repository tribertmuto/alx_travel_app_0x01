from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ListingViewSet, BookingViewSet

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'listings', ListingViewSet, basename='listing')
router.register(r'bookings', BookingViewSet, basename='booking')

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('api/', include(router.urls)),
]

# Alternative URL patterns for manual configuration (commented out)
# urlpatterns = [
#     # Listing endpoints
#     path('api/listings/', ListingViewSet.as_view({'get': 'list', 'post': 'create'}), name='listing-list'),
#     path('api/listings/<int:pk>/', ListingViewSet.as_view({
#         'get': 'retrieve',
#         'put': 'update',
#         'patch': 'partial_update',
#         'delete': 'destroy'
#     }), name='listing-detail'),
#     path('api/listings/available/', ListingViewSet.as_view({'get': 'available'}), name='listing-available'),
#     path('api/listings/by_location/', ListingViewSet.as_view({'get': 'by_location'}), name='listing-by-location'),
#     
#     # Booking endpoints
#     path('api/bookings/', BookingViewSet.as_view({'get': 'list', 'post': 'create'}), name='booking-list'),
#     path('api/bookings/<int:pk>/', BookingViewSet.as_view({
#         'get': 'retrieve',
#         'put': 'update',
#         'patch': 'partial_update',
#         'delete': 'destroy'
#     }), name='booking-detail'),
#     path('api/bookings/<int:pk>/cancel/', BookingViewSet.as_view({'post': 'cancel'}), name='booking-cancel'),
#     path('api/bookings/<int:pk>/confirm/', BookingViewSet.as_view({'post': 'confirm'}), name='booking-confirm'),
#     path('api/bookings/my_bookings/', BookingViewSet.as_view({'get': 'my_bookings'}), name='booking-my-bookings'),
# ]
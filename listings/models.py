from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class Listing(models.Model):
    """
    Model representing a property listing for booking.
    """
    PROPERTY_TYPES = [
        ('apartment', 'Apartment'),
        ('house', 'House'),
        ('condo', 'Condominium'),
        ('villa', 'Villa'),
        ('cabin', 'Cabin'),
        ('loft', 'Loft'),
        ('townhouse', 'Townhouse'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=200, help_text="Title of the property listing")
    description = models.TextField(help_text="Detailed description of the property")
    location = models.CharField(max_length=200, help_text="Property location (city, state)")
    property_type = models.CharField(
        max_length=20, 
        choices=PROPERTY_TYPES, 
        default='apartment',
        help_text="Type of property"
    )
    price_per_night = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Price per night in USD"
    )
    max_guests = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Maximum number of guests allowed"
    )
    bedrooms = models.PositiveIntegerField(
        default=1,
        help_text="Number of bedrooms"
    )
    bathrooms = models.PositiveIntegerField(
        default=1,
        help_text="Number of bathrooms"
    )
    amenities = models.TextField(
        blank=True,
        help_text="List of amenities (comma-separated)"
    )
    available = models.BooleanField(
        default=True,
        help_text="Whether the listing is available for booking"
    )
    host = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='listings',
        help_text="User who owns this listing"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['location']),
            models.Index(fields=['property_type']),
            models.Index(fields=['price_per_night']),
            models.Index(fields=['available']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.location}"
    
    @property
    def amenities_list(self):
        """
        Return amenities as a list.
        """
        if self.amenities:
            return [amenity.strip() for amenity in self.amenities.split(',')]
        return []
    
    def is_available_for_dates(self, check_in, check_out):
        """
        Check if the listing is available for the given date range.
        """
        if not self.available:
            return False
        
        from django.db.models import Q
        overlapping_bookings = self.bookings.filter(
            Q(check_in_date__lt=check_out) & Q(check_out_date__gt=check_in),
            status__in=['confirmed', 'pending']
        )
        
        return not overlapping_bookings.exists()


class Booking(models.Model):
    """
    Model representing a booking for a listing.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='bookings',
        help_text="The listing being booked"
    )
    guest = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bookings',
        help_text="User making the booking"
    )
    check_in_date = models.DateField(help_text="Check-in date")
    check_out_date = models.DateField(help_text="Check-out date")
    number_of_guests = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Number of guests for this booking"
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Total price for the booking"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Current status of the booking"
    )
    special_requests = models.TextField(
        blank=True,
        help_text="Any special requests from the guest"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['check_in_date']),
            models.Index(fields=['check_out_date']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(check_out_date__gt=models.F('check_in_date')),
                name='check_out_after_check_in'
            )
        ]
    
    def __str__(self):
        return f"Booking {self.id} - {self.listing.title} ({self.check_in_date} to {self.check_out_date})"
    
    @property
    def nights(self):
        """
        Calculate the number of nights for this booking.
        """
        return (self.check_out_date - self.check_in_date).days
    
    def calculate_total_price(self):
        """
        Calculate and update the total price based on nights and listing price.
        """
        if self.check_in_date and self.check_out_date and self.listing:
            nights = self.nights
            self.total_price = self.listing.price_per_night * nights
            self.save(update_fields=['total_price'])
        return self.total_price
    
    def clean(self):
        """
        Custom validation for the booking model.
        """
        from django.core.exceptions import ValidationError
        
        # Validate dates
        if self.check_in_date and self.check_out_date:
            if self.check_in_date >= self.check_out_date:
                raise ValidationError("Check-out date must be after check-in date.")
        
        # Validate guest capacity
        if self.listing and self.number_of_guests:
            if self.number_of_guests > self.listing.max_guests:
                raise ValidationError(
                    f"Number of guests ({self.number_of_guests}) exceeds "
                    f"listing capacity ({self.listing.max_guests})."
                )
        
        # Prevent guest from booking their own listing
        if self.listing and self.guest:
            if self.listing.host == self.guest:
                raise ValidationError("You cannot book your own listing.")
    
    def save(self, *args, **kwargs):
        """
        Override save to calculate total price and run validation.
        """
        self.full_clean()
        super().save(*args, **kwargs)
        
        # Calculate total price if not already set
        if self.total_price == 0:
            self.calculate_total_price()


class Review(models.Model):
    """
    Model for guest reviews of listings (optional enhancement).
    """
    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        related_name='review',
        help_text="The booking this review is for"
    )
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5 stars"
    )
    comment = models.TextField(
        blank=True,
        help_text="Optional review comment"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Review for {self.booking.listing.title} - {self.rating} stars"
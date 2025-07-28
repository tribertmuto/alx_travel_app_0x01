from django.db import models

class Listing(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

class Booking(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    user_name = models.CharField(max_length=100)
    booking_date = models.DateField()

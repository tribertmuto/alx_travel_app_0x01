# ALX Travel App 0x01

A Django REST API for managing travel listings and bookings with Swagger documentation.

## Features

- **Listings Management**: CRUD operations for travel listings
- **Bookings Management**: CRUD operations for travel bookings
- **RESTful API**: Follows REST conventions
- **Swagger Documentation**: Interactive API documentation
- **Filtering & Search**: Advanced query capabilities
- **Pagination**: Built-in pagination support

## API Endpoints

Base URL: `/api/`

### Listings Endpoints

- `GET /api/listings/` - List all listings (with pagination)
- `POST /api/listings/` - Create new listing
- `GET /api/listings/{id}/` - Retrieve specific listing
- `PUT /api/listings/{id}/` - Update listing
- `PATCH /api/listings/{id}/` - Partial update listing
- `DELETE /api/listings/{id}/` - Delete listing

**Query Parameters:**
- `search` - Search in title and description
- `price` - Filter by price
- `ordering` - Order by price, created_at, updated_at

### Bookings Endpoints

- `GET /api/bookings/` - List all bookings (with pagination)
- `POST /api/bookings/` - Create new booking
- `GET /api/bookings/{id}/` - Retrieve specific booking
- `PUT /api/bookings/{id}/` - Update booking
- `PATCH /api/bookings/{id}/` - Partial update booking
- `DELETE /api/bookings/{id}/` - Delete booking

**Query Parameters:**
- `search` - Search in user_name
- `listing` - Filter by listing ID
- `booking_date` - Filter by booking date
- `ordering` - Order by booking_date, created_at, updated_at

## Documentation

- **Swagger UI**: Available at `/swagger/`
- **API Root**: Available at `/api/`

## Setup Instructions

1. **Install Dependencies:**
   ```bash
   pip install django djangorestframework drf-yasg django-filter
   ```

2. **Run Migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **Create Superuser (Optional):**
   ```bash
   python manage.py createsuperuser
   ```

4. **Run Development Server:**
   ```bash
   python manage.py runserver
   ```

## Testing with Postman

### Create a Listing
```
POST /api/listings/
Content-Type: application/json

{
    "title": "Beach House in Miami",
    "description": "Beautiful beachfront property with ocean views",
    "price": "250.00"
}
```

### Create a Booking
```
POST /api/bookings/
Content-Type: application/json

{
    "listing": 1,
    "user_name": "John Doe",
    "booking_date": "2024-01-15"
}
```

### Get All Listings
```
GET /api/listings/
```

### Get All Bookings
```
GET /api/bookings/
```

## Model Structure

### Listing Model
- `id` - Primary key
- `title` - Listing title (max 100 chars)
- `description` - Listing description
- `price` - Decimal price
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp

### Booking Model
- `id` - Primary key
- `listing` - Foreign key to Listing
- `user_name` - Customer name (max 100 chars)
- `booking_date` - Date of booking
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp

## Technologies Used

- **Django** - Web framework
- **Django REST Framework** - API framework
- **drf-yasg** - Swagger documentation
- **django-filter** - Advanced filtering
- **SQLite** - Database (default)

# ALX Travel App API - Listings and Bookings

## Project Overview

This project (`alx_travel_app_0x01`) is an enhanced version of `alx_travel_app_0x00` with comprehensive API development for managing listings and bookings using Django REST Framework.

## Features

- **RESTful API** for Listings and Bookings management
- **CRUD operations** for both models
- **Authentication and Permissions** system
- **Advanced filtering and search** capabilities
- **Swagger/OpenAPI documentation**
- **Custom actions** for business logic
- **Comprehensive error handling**

## Project Structure

```
alx_travel_app/
├── listings/
│   ├── views.py          # API ViewSets
│   ├── urls.py           # URL configuration
│   ├── models.py         # Data models
│   ├── serializers.py    # DRF serializers
│   └── migrations/
├── requirements.txt      # Python dependencies
├── manage.py
└── README.md
```

## API Endpoints

### Listings API

| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| `GET` | `/api/listings/` | List all listings | Optional |
| `POST` | `/api/listings/` | Create new listing | Required |
| `GET` | `/api/listings/{id}/` | Retrieve specific listing | Optional |
| `PUT` | `/api/listings/{id}/` | Update listing | Required (Owner) |
| `PATCH` | `/api/listings/{id}/` | Partial update listing | Required (Owner) |
| `DELETE` | `/api/listings/{id}/` | Delete listing | Required (Owner) |
| `GET` | `/api/listings/available/` | Get available listings by date | Optional |
| `GET` | `/api/listings/by_location/` | Filter listings by location | Optional |

### Bookings API

| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| `GET` | `/api/bookings/` | List user's bookings | Required |
| `POST` | `/api/bookings/` | Create new booking | Required |
| `GET` | `/api/bookings/{id}/` | Retrieve specific booking | Required |
| `PUT` | `/api/bookings/{id}/` | Update booking | Required (Owner) |
| `PATCH` | `/api/bookings/{id}/` | Partial update booking | Required (Owner) |
| `DELETE` | `/api/bookings/{id}/` | Delete booking | Required (Owner) |
| `POST` | `/api/bookings/{id}/cancel/` | Cancel booking | Required (Owner/Host) |
| `POST` | `/api/bookings/{id}/confirm/` | Confirm booking | Required (Host) |
| `GET` | `/api/bookings/my_bookings/` | Get user's booking history | Required |

## Setup Instructions

### 1. Project Duplication

```bash
# Clone or copy the previous project
cp -r alx_travel_app_0x00 alx_travel_app_0x01
cd alx_travel_app_0x01
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Required Dependencies

Add these to your `requirements.txt`:

```txt
Django>=4.2.0
djangorestframework>=3.14.0
django-filter>=23.2
drf-yasg>=1.21.7
djangorestframework-simplejwt>=5.3.0
```

### 4. Django Settings Configuration

Add to your `settings.py`:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'django_filters',
    'drf_yasg',
    'listings',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# Swagger settings
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    }
}
```

### 5. Update Main URLs

In your main `urls.py`:

```python
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="ALX Travel App API",
        default_version='v1',
        description="API for managing travel listings and bookings",
        terms_of_service="https://www.example.com/policies/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('listings.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
```

### 6. Database Migration

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 7. Run Development Server

```bash
python manage.py runserver
```

## API Testing

### Using Postman

1. **Authentication Setup**:
   - Create a user account via admin or registration endpoint
   - Obtain JWT token from `/auth/token/` endpoint
   - Add `Authorization: Bearer <token>` header to authenticated requests

2. **Test Endpoints**:

#### Create Listing (POST)
```
URL: http://localhost:8000/api/listings/
Method: POST
Headers: Authorization: Bearer <your-token>
Body (JSON):
{
    "title": "Beautiful Beach House",
    "description": "A stunning beachfront property",
    "location": "Miami, FL",
    "property_type": "house",
    "price_per_night": 150.00,
    "max_guests": 6,
    "bedrooms": 3,
    "bathrooms": 2
}
```

#### Get Available Listings (GET)
```
URL: http://localhost:8000/api/listings/available/?check_in=2024-12-01&check_out=2024-12-07
Method: GET
```

#### Create Booking (POST)
```
URL: http://localhost:8000/api/bookings/
Method: POST
Headers: Authorization: Bearer <your-token>
Body (JSON):
{
    "listing": 1,
    "check_in_date": "2024-12-01",
    "check_out_date": "2024-12-07",
    "number_of_guests": 4,
    "special_requests": "Late check-in please"
}
```

### Using cURL

```bash
# Get all listings
curl -X GET http://localhost:8000/api/listings/

# Create a listing (with authentication)
curl -X POST http://localhost:8000/api/listings/ \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Mountain Cabin",
    "description": "Cozy cabin in the mountains",
    "location": "Aspen, CO",
    "property_type": "cabin",
    "price_per_night": 200.00
  }'

# Get available listings
curl -X GET "http://localhost:8000/api/listings/available/?check_in=2024-12-01&check_out=2024-12-07"
```

## API Documentation

### Swagger UI
Visit `http://localhost:8000/swagger/` for interactive API documentation

### ReDoc
Visit `http://localhost:8000/redoc/` for alternative documentation format

## API Features

### Filtering and Search

- **Listings**: Filter by location, property_type, price_per_night
- **Search**: Search listings by title, description, location
- **Ordering**: Sort by created_at, price_per_night, rating

### Custom Actions

#### Listings
- `available/`: Get listings available for specific dates
- `by_location/`: Filter listings by location

#### Bookings
- `cancel/`: Cancel a booking
- `confirm/`: Confirm a pending booking (host only)
- `my_bookings/`: Get user's booking history

### Permissions

- **Listings**: 
  - Read: Public access
  - Create/Update/Delete: Authenticated users (owners only)
- **Bookings**: 
  - All operations: Authenticated users
  - Users can only see their own bookings
  - Hosts can confirm bookings for their listings

## Error Handling

The API returns appropriate HTTP status codes:

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error

Error responses include detailed messages:

```json
{
    "error": "Description of the error",
    "field_errors": {
        "field_name": ["Specific field error message"]
    }
}
```

## Development Notes

### Models Required

Ensure your `models.py` includes:

```python
# Listing model with fields: title, description, location, property_type, price_per_night, host, etc.
# Booking model with fields: listing, guest, check_in_date, check_out_date, status, etc.
```

### Serializers Required

Create `serializers.py` with:

```python
# ListingSerializer for listing data validation and serialization
# BookingSerializer for booking data validation and serialization
```

## Deployment Considerations

1. **Environment Variables**: Use environment variables for sensitive settings
2. **CORS**: Configure CORS headers for frontend integration
3. **Rate Limiting**: Implement rate limiting for production
4. **Caching**: Add caching for frequently accessed endpoints
5. **Monitoring**: Set up API monitoring and logging

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests
5. Submit a pull request

## License

This project is licensed under the MIT License.
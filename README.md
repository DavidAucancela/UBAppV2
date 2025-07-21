# Universal Box Shipment Registration System

A comprehensive web storage and search system for managing Universal Box's shipment records. Built with Django REST Framework (backend) and Angular (frontend).

## Features

### User Management
- **CRUD Operations**: Complete user account management
- **Role-Based Access Control**: Admin, Manager, Operator, and Viewer roles
- **Special User Conditions**: Support for users with disabilities
- **JWT Authentication**: Secure token-based authentication

### Shipment Archives
- **Shipment Creation**: Create shipments with multiple products
- **Bulk Import**: Import shipments from JSON files with automatic data cleansing
- **Archive Management**: Mark and archive shipments
- **Product Management**: Detailed product information for each shipment

### Search Functionality
- **Advanced Search**: Query shipments by multiple parameters
- **Filtering Options**: Filter by status, priority, dates, and more
- **Real-time Search**: Fast and efficient search capabilities

### Dashboard and Visualization
- **Interactive Dashboard**: Real-time metrics and insights
- **Data Visualization**: Charts and graphs for shipment analytics
- **Export Capabilities**: Export data in various formats

## Technology Stack

### Backend
- Django 5.2.4
- Django REST Framework
- PostgreSQL
- JWT Authentication
- Pandas for data processing

### Frontend
- Angular 19
- TypeScript
- SCSS
- Chart.js for visualizations
- Angular Material UI

## Installation

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+

### Backend Setup

1. Clone the repository:
```bash
cd universal-box-system
```

2. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your database credentials
```

5. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

6. Create superuser:
```bash
python manage.py createsuperuser
```

7. Run the development server:
```bash
python manage.py runserver
```

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
ng serve
```

The application will be available at `http://localhost:4200`

## API Documentation

### Authentication Endpoints
- `POST /api/auth/login/` - User login
- `POST /api/auth/refresh/` - Refresh JWT token

### User Management Endpoints
- `GET /api/users/` - List all users
- `POST /api/users/` - Create new user
- `GET /api/users/{id}/` - Get user details
- `PUT /api/users/{id}/` - Update user
- `DELETE /api/users/{id}/` - Delete user
- `GET /api/users/me/` - Get current user
- `POST /api/users/change_password/` - Change password
- `POST /api/users/{id}/update_role/` - Update user role

### Shipment Endpoints
- `GET /api/shipments/` - List all shipments
- `POST /api/shipments/` - Create new shipment
- `GET /api/shipments/{id}/` - Get shipment details
- `PUT /api/shipments/{id}/` - Update shipment
- `DELETE /api/shipments/{id}/` - Delete shipment
- `POST /api/shipments/{id}/archive/` - Archive shipment
- `POST /api/shipments/{id}/unarchive/` - Unarchive shipment
- `POST /api/shipments/bulk_import/` - Bulk import from JSON
- `GET /api/shipments/search/` - Search shipments
- `GET /api/shipments/statistics/` - Get shipment statistics

### Product Endpoints
- `GET /api/products/` - List all products
- `POST /api/products/` - Create new product
- `GET /api/products/{id}/` - Get product details
- `PUT /api/products/{id}/` - Update product
- `DELETE /api/products/{id}/` - Delete product

## Usage

### Bulk Import Format

Create a JSON file with the following structure:

```json
[
  {
    "sender_name": "John Smith",
    "sender_company": "Tech Solutions Inc",
    "sender_address": "123 Main Street",
    "sender_city": "New York",
    "sender_state": "NY",
    "sender_zip": "10001",
    "sender_country": "USA",
    "sender_phone": "+1-212-555-0123",
    "sender_email": "john.smith@techsolutions.com",
    "recipient_name": "Jane Doe",
    "recipient_company": "ABC Corporation",
    "recipient_address": "456 Oak Avenue",
    "recipient_city": "Los Angeles",
    "recipient_state": "CA",
    "recipient_zip": "90001",
    "recipient_country": "USA",
    "recipient_phone": "+1-323-555-0456",
    "recipient_email": "jane.doe@abccorp.com",
    "weight": 5.5,
    "dimensions": "30x20x15",
    "value": 250.00,
    "insurance_amount": 50.00,
    "shipping_cost": 25.00,
    "priority": "HIGH",
    "products": [
      {
        "name": "Laptop Computer",
        "description": "High-performance business laptop",
        "category": "ELECTRONICS",
        "sku": "LAP-001",
        "quantity": 1,
        "unit_price": 1200.00,
        "weight": 2.5,
        "is_fragile": true
      }
    ]
  }
]
```

### User Roles and Permissions

- **Admin**: Full system access
- **Manager**: Can manage shipments and view all data
- **Operator**: Can create and edit shipments
- **Viewer**: Read-only access

## Development

### Running Tests

Backend tests:
```bash
python manage.py test
```

Frontend tests:
```bash
cd frontend
ng test
```

### Code Style

- Backend: Follow PEP 8
- Frontend: Follow Angular style guide

## Deployment

### Production Environment Variables

```
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com
DB_ENGINE=django.db.backends.postgresql
DB_NAME=universal_box_prod
DB_USER=postgres
DB_PASSWORD=secure-password
DB_HOST=localhost
DB_PORT=5432
CORS_ALLOWED_ORIGINS=https://your-domain.com
```

### Docker Deployment

Docker files are included for easy deployment. Run:

```bash
docker-compose up -d
```

## License

This project is proprietary software for Universal Box.

## Support

For support, email support@universalbox.com
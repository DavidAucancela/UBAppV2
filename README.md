# Universal Box Shipment Registration System

A comprehensive web storage and search system for Universal Box's shipment registration, built with Django REST Framework (backend) and Angular (frontend).

## 🚀 Features

### 🔐 User Management
- **CRUD Operations**: Complete user lifecycle management
- **Role-Based Access Control**: 4 user roles (Admin, Gerente, Digitador, Comprador)
- **Permission System**: Granular permissions based on user roles
- **Authentication**: Token-based authentication with JWT
- **User Dashboard**: Personalized dashboard based on user role

### 📦 Shipment Archives
- **New Shipment Creation**: Create shipments with multiple products
- **Bulk Import**: Import shipments from JSON and Excel files
- **Data Quality**: Automatic data cleansing during import
- **Record Management**: Archive and manage shipment records
- **Product Management**: Detailed product information with categories
- **Status Tracking**: Track shipment status throughout lifecycle

### 🔍 Advanced Search
- **Multi-criteria Search**: Search across shipments, products, and users
- **Filtering Options**: Advanced filtering by status, date, category, etc.
- **Search History**: Track and manage search history
- **Real-time Results**: Instant search results with pagination

### 📊 Dashboard and Analytics
- **Interactive Dashboard**: Real-time metrics and KPIs
- **Data Visualization**: Charts and graphs using Chart.js
- **Comprehensive Reports**: Generate detailed reports (PDF/Excel)
- **User Activity Tracking**: Monitor user actions and system usage
- **Financial Analytics**: Revenue and cost analysis
- **Performance Metrics**: System performance monitoring

### 🔧 Integration Features
- **RESTful APIs**: Well-documented REST API endpoints
- **Real-time Updates**: Live data updates using WebSocket connections
- **File Upload/Download**: Support for various file formats
- **Export Capabilities**: Export data in multiple formats
- **Audit Trail**: Complete audit log of all system activities

## 🏗️ System Architecture

### Backend (Django REST Framework)
```
backend/
├── DRF_APP_BACKEND/
│   ├── DRF_APP_BACKEND/          # Main project settings
│   ├── usuarios/                 # User management app
│   ├── archivos/                 # Shipment and product management
│   ├── busqueda/                 # Search functionality
│   ├── dashboard/                # Analytics and reporting
│   ├── manage.py
│   └── requirements.txt
└── venv/                         # Virtual environment
```

### Frontend (Angular)
```
frontend/
└── ANGULAR_FRONTEND/
    ├── src/
    │   ├── app/
    │   │   ├── components/        # UI components
    │   │   ├── services/          # API services
    │   │   ├── models/            # TypeScript interfaces
    │   │   └── guards/            # Route guards
    │   └── environments/          # Environment configs
    ├── package.json
    └── angular.json
```

## 🛠️ Installation and Setup

### Prerequisites
- Python 3.13+
- Node.js 18+
- npm 8+
- Git

### Backend Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd universal-box-system
```

2. **Create and activate virtual environment**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

4. **Run database migrations**
```bash
cd DRF_APP_BACKEND
python manage.py makemigrations
python manage.py migrate
```

5. **Create superuser**
```bash
python manage.py createsuperuser
```

6. **Start the Django development server**
```bash
python manage.py runserver 0.0.0.0:8000
```

### Frontend Setup

1. **Navigate to frontend directory**
```bash
cd frontend/ANGULAR_FRONTEND
```

2. **Install Node.js dependencies**
```bash
npm install
```

3. **Start the Angular development server**
```bash
npm start
```

The application will be available at:
- **Frontend**: http://localhost:4200
- **Backend API**: http://localhost:8000/api
- **Admin Panel**: http://localhost:8000/admin

## 📱 User Roles and Permissions

### 👑 Admin (Rol 1)
- Full system access
- User management (CRUD)
- All shipment operations
- System configuration
- Reports and analytics
- Audit logs

### 🏢 Gerente (Rol 2)
- User management (limited)
- All shipment operations
- Reports and analytics
- Team oversight
- Performance monitoring

### ✍️ Digitador (Rol 3)
- Shipment creation and editing
- Product management
- Data entry operations
- Basic reporting
- Search functionality

### 🛒 Comprador (Rol 4)
- View own shipments only
- Track shipment status
- Basic search
- Personal dashboard
- Order history

## 🔌 API Endpoints

### Authentication
```
POST /api/usuarios/login/          # User login
POST /api/usuarios/logout/         # User logout
GET  /api/usuarios/profile/        # User profile
```

### Users
```
GET    /api/usuarios/              # List users
POST   /api/usuarios/              # Create user
GET    /api/usuarios/{id}/         # Get user
PUT    /api/usuarios/{id}/         # Update user
DELETE /api/usuarios/{id}/         # Delete user
```

### Shipments
```
GET    /api/envios/                # List shipments
POST   /api/envios/                # Create shipment
GET    /api/envios/{id}/           # Get shipment
PUT    /api/envios/{id}/           # Update shipment
DELETE /api/envios/{id}/           # Delete shipment
POST   /api/envios/import_json/    # Import from JSON
POST   /api/envios/import_excel/   # Import from Excel
```

### Dashboard
```
GET  /api/dashboard/stats/         # Dashboard statistics
GET  /api/dashboard/metrics-summary/ # Metrics summary
GET  /api/dashboard/reports/       # List reports
POST /api/dashboard/reports/       # Create report
```

### Search
```
GET  /api/busqueda/buscar/         # Search functionality
GET  /api/busqueda/               # Search history
```

## 📊 Dashboard Features

### Key Performance Indicators (KPIs)
- Total shipments and growth rate
- Total products and categories
- Financial metrics and revenue
- Active users and engagement
- System performance metrics

### Interactive Charts
- **Line Charts**: Trends over time
- **Pie Charts**: Distribution analysis
- **Bar Charts**: Comparative analysis
- **Real-time Updates**: Live data refresh

### Report Generation
- **Shipment Summary**: Comprehensive shipment analysis
- **Product Analysis**: Product performance metrics
- **User Activity**: User engagement reports
- **Financial Summary**: Revenue and cost analysis
- **Custom Reports**: Configurable report parameters

## 🔄 Data Import/Export

### Supported Import Formats
- **JSON**: Structured data import with validation
- **Excel**: Spreadsheet import with error handling
- **CSV**: Comma-separated values support

### Export Capabilities
- **PDF Reports**: Professional formatted reports
- **Excel Export**: Data export for analysis
- **JSON Export**: API data export
- **CSV Export**: Spreadsheet compatible format

### Data Validation
- **Schema Validation**: Ensure data integrity
- **Error Reporting**: Detailed error messages
- **Data Cleansing**: Automatic data cleanup
- **Duplicate Detection**: Prevent data duplication

## 🔒 Security Features

### Authentication & Authorization
- **Token-based Authentication**: Secure API access
- **Role-based Permissions**: Granular access control
- **Session Management**: Secure session handling
- **Password Security**: Strong password requirements

### Data Protection
- **Input Validation**: Prevent injection attacks
- **CORS Configuration**: Cross-origin security
- **Rate Limiting**: API abuse prevention
- **Audit Logging**: Complete activity tracking

## 🚀 Deployment

### Production Setup

1. **Environment Configuration**
```bash
# Set production environment variables
export DJANGO_SETTINGS_MODULE=DRF_APP_BACKEND.settings.production
export SECRET_KEY=your-secret-key
export DATABASE_URL=your-database-url
```

2. **Database Setup**
```bash
python manage.py migrate
python manage.py collectstatic
```

3. **Web Server Configuration**
- Configure Nginx/Apache
- Set up SSL certificates
- Configure domain routing

### Docker Deployment
```dockerfile
# Dockerfile example for Django
FROM python:3.13
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

## 🧪 Testing

### Backend Tests
```bash
cd backend/DRF_APP_BACKEND
python manage.py test
```

### Frontend Tests
```bash
cd frontend/ANGULAR_FRONTEND
npm test
npm run e2e
```

### API Testing
- Use tools like Postman or curl
- Test authentication endpoints
- Validate data operations
- Check error handling

## 📈 Performance Optimization

### Database Optimization
- **Indexing**: Optimized database indexes
- **Query Optimization**: Efficient database queries
- **Connection Pooling**: Database connection management
- **Caching**: Redis/Memcached integration

### Frontend Optimization
- **Lazy Loading**: Component lazy loading
- **Code Splitting**: Bundle optimization
- **Caching**: Browser caching strategies
- **Minification**: Asset optimization

## 🐛 Troubleshooting

### Common Issues

1. **CORS Errors**
   - Check CORS_ALLOWED_ORIGINS in settings
   - Verify frontend URL configuration

2. **Authentication Issues**
   - Check token expiration
   - Verify user permissions

3. **Database Connection**
   - Check database credentials
   - Verify database server status

4. **File Upload Issues**
   - Check file size limits
   - Verify media directory permissions

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

### Development Guidelines
- Follow PEP 8 for Python code
- Use TypeScript for Angular components
- Write comprehensive tests
- Document new features
- Follow Git commit conventions

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Support

For support and questions:
- Create an issue on GitHub
- Contact the development team
- Check the documentation wiki

## 🔄 Changelog

### Version 1.0.0
- Initial release
- User management system
- Shipment registration
- Advanced search functionality
- Dashboard and analytics
- Import/export capabilities
- Role-based access control

---

**Universal Box Shipment Registration System** - Comprehensive solution for modern logistics management.
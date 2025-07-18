# WhatsApp Service Booking Workflow

A comprehensive intelligent WhatsApp-based service booking system that revolutionizes customer service automation through advanced natural language processing, intelligent supplier matching, and seamless workflow orchestration.

## Features

- **Intelligent Message Processing**: Advanced natural language understanding with OpenAI GPT-4
- **Customer Management**: Comprehensive authentication and profile management
- **Service Identification**: AI-powered service recognition with confidence scoring
- **Supplier Matching**: Advanced algorithms for optimal supplier selection
- **Escalation Management**: Intelligent human handoff when needed
- **Security Framework**: Comprehensive data protection and compliance
- **Performance Monitoring**: Real-time analytics and optimization

## Technology Stack

- **Backend**: FastAPI with Python
- **Database**: PostgreSQL (in-memory for development)
- **AI**: OpenAI GPT-4 for natural language processing
- **Messaging**: WhatsApp Business API
- **Workflow**: n8n automation platform integration
- **Authentication**: JWT-based security

## Quick Start

1. **Install Dependencies**
   ```bash
   cd backend
   poetry install
   ```

2. **Environment Setup**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Run the Application**
   ```bash
   poetry run fastapi dev app/main.py
   ```

4. **Access the API**
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## Environment Variables

```env
# WhatsApp Business API
WHATSAPP_ACCESS_TOKEN=your_whatsapp_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
WHATSAPP_WEBHOOK_VERIFY_TOKEN=your_webhook_verify_token

# OpenAI
OPENAI_API_KEY=your_openai_api_key

# Database
DATABASE_URL=postgresql://user:password@localhost/dbname

# Security
JWT_SECRET_KEY=your_jwt_secret_key
WEBHOOK_SECRET=your_webhook_secret
```

## API Endpoints

### Core Endpoints
- `POST /webhook/whatsapp` - WhatsApp webhook for incoming messages
- `GET /webhook/whatsapp` - WhatsApp webhook verification
- `GET /health` - Health check endpoint

### Customer Management
- `GET /customers/{rfc}` - Get customer profile
- `PUT /customers/{rfc}` - Update customer profile

### Service Management
- `GET /services` - List available services
- `POST /services/identify` - Identify service from text

### Supplier Management
- `GET /suppliers` - List suppliers
- `POST /suppliers/match` - Match suppliers for service

### Booking Management
- `GET /bookings` - List bookings
- `POST /bookings` - Create new booking
- `PUT /bookings/{id}` - Update booking status

## Architecture

The system follows a microservices architecture with clear separation of concerns:

1. **Message Processing Layer**: Handles WhatsApp message reception and parsing
2. **Intelligence Layer**: AI-powered service identification and decision making
3. **Business Logic Layer**: Customer management, supplier matching, booking workflow
4. **Data Layer**: Database operations and state management
5. **Integration Layer**: External API communications

## Implementation Phases

1. **Phase 1**: Core infrastructure and basic workflow
2. **Phase 2**: AI integration and service identification
3. **Phase 3**: Supplier management and communication
4. **Phase 4**: Advanced features and analytics

## Security

- End-to-end encryption for all communications
- JWT-based authentication and authorization
- Input validation and sanitization
- Rate limiting and abuse prevention
- GDPR and CCPA compliance

## Monitoring

- Real-time performance metrics
- Customer satisfaction tracking
- Supplier performance analytics
- System health monitoring
- Business intelligence reporting

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.

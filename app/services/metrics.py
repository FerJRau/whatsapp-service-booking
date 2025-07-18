import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import asyncio
from prometheus_client import Counter, Histogram, Gauge, start_http_server

logger = logging.getLogger(__name__)

class MetricsService:
    """Service for collecting and exposing application metrics"""
    
    def __init__(self):
        self.messages_processed = Counter(
            'whatsapp_messages_processed_total',
            'Total number of WhatsApp messages processed',
            ['direction', 'message_type']
        )
        
        self.message_processing_time = Histogram(
            'whatsapp_message_processing_seconds',
            'Time spent processing WhatsApp messages'
        )
        
        self.active_sessions = Gauge(
            'whatsapp_active_sessions',
            'Number of currently active sessions'
        )
        
        self.sessions_created = Counter(
            'whatsapp_sessions_created_total',
            'Total number of sessions created'
        )
        
        self.sessions_completed = Counter(
            'whatsapp_sessions_completed_total',
            'Total number of sessions completed',
            ['completion_type']
        )
        
        self.service_identifications = Counter(
            'whatsapp_service_identifications_total',
            'Total number of service identification attempts',
            ['confidence_level']
        )
        
        self.service_identification_accuracy = Histogram(
            'whatsapp_service_identification_confidence',
            'Confidence scores for service identification'
        )
        
        self.supplier_matches = Counter(
            'whatsapp_supplier_matches_total',
            'Total number of supplier matching attempts',
            ['success']
        )
        
        self.supplier_response_time = Histogram(
            'whatsapp_supplier_response_seconds',
            'Time for suppliers to respond to requests'
        )
        
        self.bookings_created = Counter(
            'whatsapp_bookings_created_total',
            'Total number of bookings created',
            ['priority']
        )
        
        self.bookings_completed = Counter(
            'whatsapp_bookings_completed_total',
            'Total number of bookings completed',
            ['status']
        )
        
        self.escalations = Counter(
            'whatsapp_escalations_total',
            'Total number of escalations to human agents',
            ['reason']
        )
        
        self.escalation_resolution_time = Histogram(
            'whatsapp_escalation_resolution_seconds',
            'Time to resolve escalated sessions'
        )
        
        self.errors = Counter(
            'whatsapp_errors_total',
            'Total number of errors',
            ['error_type', 'component']
        )
        
        self.customer_ratings = Histogram(
            'whatsapp_customer_ratings',
            'Customer satisfaction ratings',
            buckets=[1, 2, 3, 4, 5]
        )
        
        self.api_request_duration = Histogram(
            'whatsapp_api_request_duration_seconds',
            'Duration of API requests',
            ['endpoint', 'method']
        )
        
        self.database_query_duration = Histogram(
            'whatsapp_database_query_duration_seconds',
            'Duration of database queries',
            ['operation']
        )
    
    def record_message_processed(self, direction: str, message_type: str, processing_time: float):
        """Record message processing metrics"""
        self.messages_processed.labels(direction=direction, message_type=message_type).inc()
        self.message_processing_time.observe(processing_time)
    
    def record_session_created(self):
        """Record session creation"""
        self.sessions_created.inc()
        self.active_sessions.inc()
    
    def record_session_completed(self, completion_type: str):
        """Record session completion"""
        self.sessions_completed.labels(completion_type=completion_type).inc()
        self.active_sessions.dec()
    
    def record_service_identification(self, confidence_score: int):
        """Record service identification attempt"""
        confidence_level = "high" if confidence_score >= 80 else "medium" if confidence_score >= 50 else "low"
        self.service_identifications.labels(confidence_level=confidence_level).inc()
        self.service_identification_accuracy.observe(confidence_score / 100.0)
    
    def record_supplier_match(self, success: bool, response_time: Optional[float] = None):
        """Record supplier matching attempt"""
        self.supplier_matches.labels(success=str(success).lower()).inc()
        if response_time is not None:
            self.supplier_response_time.observe(response_time)
    
    def record_booking_created(self, priority: str):
        """Record booking creation"""
        self.bookings_created.labels(priority=priority).inc()
    
    def record_booking_completed(self, status: str):
        """Record booking completion"""
        self.bookings_completed.labels(status=status).inc()
    
    def record_escalation(self, reason: str, resolution_time: Optional[float] = None):
        """Record escalation to human agent"""
        self.escalations.labels(reason=reason).inc()
        if resolution_time is not None:
            self.escalation_resolution_time.observe(resolution_time)
    
    def record_error(self, error_type: str, component: str):
        """Record error occurrence"""
        self.errors.labels(error_type=error_type, component=component).inc()
    
    def record_customer_rating(self, rating: float):
        """Record customer satisfaction rating"""
        self.customer_ratings.observe(rating)
    
    def record_api_request(self, endpoint: str, method: str, duration: float):
        """Record API request metrics"""
        self.api_request_duration.labels(endpoint=endpoint, method=method).observe(duration)
    
    def record_database_query(self, operation: str, duration: float):
        """Record database query metrics"""
        self.database_query_duration.labels(operation=operation).observe(duration)
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get current metrics summary"""
        return {
            "active_sessions": self.active_sessions._value._value,
            "total_messages_processed": sum(
                metric.samples[0].value for metric in self.messages_processed.collect()
                for sample in metric.samples
            ),
            "total_sessions_created": sum(
                sample.value for metric in self.sessions_created.collect()
                for sample in metric.samples
            ),
            "total_bookings_created": sum(
                sample.value for metric in self.bookings_created.collect()
                for sample in metric.samples
            ),
            "total_escalations": sum(
                sample.value for metric in self.escalations.collect()
                for sample in metric.samples
            ),
            "total_errors": sum(
                sample.value for metric in self.errors.collect()
                for sample in metric.samples
            )
        }
    
    def start_metrics_server(self, port: int = 9090):
        """Start Prometheus metrics server"""
        try:
            start_http_server(port)
            logger.info(f"Metrics server started on port {port}")
        except Exception as e:
            logger.error(f"Failed to start metrics server: {e}")

metrics = MetricsService()

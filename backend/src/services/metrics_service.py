"""
Metrics service for tracking response times and performance (T092).

Tracks p95 latency, request counts, and error rates for monitoring.
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
from collections import deque
import statistics
import logging

logger = logging.getLogger(__name__)


class MetricsService:
    """
    Service for tracking performance metrics.

    Features:
    - P95 latency tracking
    - Request count tracking
    - Error rate monitoring
    - Rolling window (last 1000 requests)
    """

    def __init__(self, window_size: int = 1000):
        """
        Initialize metrics service.

        Args:
            window_size: Number of recent requests to track (default: 1000)
        """
        self.window_size = window_size
        self.response_times: deque = deque(maxlen=window_size)
        self.request_count = 0
        self.error_count = 0
        self.start_time = datetime.now()

        logger.info(f"Metrics service initialized: window_size={window_size}")

    def record_response_time(self, duration_ms: float, error: bool = False):
        """
        Record response time for a request.

        Args:
            duration_ms: Response time in milliseconds
            error: Whether the request resulted in an error
        """
        self.response_times.append(duration_ms)
        self.request_count += 1

        if error:
            self.error_count += 1

        logger.debug(f"Recorded response time: {duration_ms:.2f}ms (error={error})")

    def get_p95_latency(self) -> float:
        """
        Calculate P95 latency from recent requests.

        Returns:
            P95 latency in milliseconds (0 if no data)
        """
        if not self.response_times:
            return 0.0

        sorted_times = sorted(self.response_times)
        p95_index = int(len(sorted_times) * 0.95)

        return sorted_times[p95_index] if p95_index < len(sorted_times) else sorted_times[-1]

    def get_p50_latency(self) -> float:
        """
        Calculate P50 (median) latency.

        Returns:
            P50 latency in milliseconds
        """
        if not self.response_times:
            return 0.0

        return statistics.median(self.response_times)

    def get_avg_latency(self) -> float:
        """
        Calculate average latency.

        Returns:
            Average latency in milliseconds
        """
        if not self.response_times:
            return 0.0

        return statistics.mean(self.response_times)

    def get_error_rate(self) -> float:
        """
        Calculate error rate as percentage.

        Returns:
            Error rate (0-100)
        """
        if self.request_count == 0:
            return 0.0

        return (self.error_count / self.request_count) * 100

    def get_requests_per_minute(self) -> float:
        """
        Calculate requests per minute.

        Returns:
            Requests per minute
        """
        uptime_minutes = (datetime.now() - self.start_time).total_seconds() / 60

        if uptime_minutes == 0:
            return 0.0

        return self.request_count / uptime_minutes

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get all metrics.

        Returns:
            Dict with all performance metrics
        """
        return {
            'request_count': self.request_count,
            'error_count': self.error_count,
            'error_rate_percent': round(self.get_error_rate(), 2),
            'latency_ms': {
                'p50': round(self.get_p50_latency(), 2),
                'p95': round(self.get_p95_latency(), 2),
                'avg': round(self.get_avg_latency(), 2),
                'min': round(min(self.response_times), 2) if self.response_times else 0,
                'max': round(max(self.response_times), 2) if self.response_times else 0,
            },
            'requests_per_minute': round(self.get_requests_per_minute(), 2),
            'uptime_seconds': int((datetime.now() - self.start_time).total_seconds()),
            'window_size': self.window_size,
            'samples_in_window': len(self.response_times),
        }

    def reset(self):
        """Reset all metrics."""
        self.response_times.clear()
        self.request_count = 0
        self.error_count = 0
        self.start_time = datetime.now()
        logger.info("Metrics reset")


# Global metrics service instance
metrics_service = MetricsService(window_size=1000)

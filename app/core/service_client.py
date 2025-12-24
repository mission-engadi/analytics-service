"""
HTTP Client for inter-service communication.

Handles authentication, retries, timeouts, and error handling
for calls to other microservices.
"""
import httpx
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class ServiceClient:
    """HTTP client for calling other microservices."""
    
    def __init__(self, timeout: int = 30, max_retries: int = 3):
        """
        Initialize service client.
        
        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self._client: Optional[httpx.AsyncClient] = None
        
    async def __aenter__(self):
        """Context manager entry."""
        self._client = httpx.AsyncClient(
            timeout=self.timeout,
            follow_redirects=True
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self._client:
            await self._client.aclose()
    
    async def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        auth_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Make GET request to service.
        
        Args:
            url: Full URL to request
            params: Query parameters
            headers: Request headers
            auth_token: Authentication token
            
        Returns:
            Response data as dictionary
            
        Raises:
            httpx.HTTPError: On request failure
        """
        if not self._client:
            raise RuntimeError("Client not initialized. Use 'async with' context.")
            
        request_headers = headers or {}
        if auth_token:
            request_headers["Authorization"] = f"Bearer {auth_token}"
        
        retries = 0
        last_exception = None
        
        while retries < self.max_retries:
            try:
                response = await self._client.get(
                    url,
                    params=params,
                    headers=request_headers
                )
                response.raise_for_status()
                return response.json()
                
            except httpx.HTTPError as e:
                last_exception = e
                retries += 1
                logger.warning(
                    f"GET request failed (attempt {retries}/{self.max_retries}): {url}",
                    exc_info=True
                )
                if retries < self.max_retries:
                    await self._wait_before_retry(retries)
        
        logger.error(f"GET request failed after {self.max_retries} attempts: {url}")
        raise last_exception
    
    async def post(
        self,
        url: str,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        auth_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Make POST request to service.
        
        Args:
            url: Full URL to request
            json: JSON request body
            data: Form data
            headers: Request headers
            auth_token: Authentication token
            
        Returns:
            Response data as dictionary
            
        Raises:
            httpx.HTTPError: On request failure
        """
        if not self._client:
            raise RuntimeError("Client not initialized. Use 'async with' context.")
            
        request_headers = headers or {}
        if auth_token:
            request_headers["Authorization"] = f"Bearer {auth_token}"
        
        retries = 0
        last_exception = None
        
        while retries < self.max_retries:
            try:
                response = await self._client.post(
                    url,
                    json=json,
                    data=data,
                    headers=request_headers
                )
                response.raise_for_status()
                return response.json()
                
            except httpx.HTTPError as e:
                last_exception = e
                retries += 1
                logger.warning(
                    f"POST request failed (attempt {retries}/{self.max_retries}): {url}",
                    exc_info=True
                )
                if retries < self.max_retries:
                    await self._wait_before_retry(retries)
        
        logger.error(f"POST request failed after {self.max_retries} attempts: {url}")
        raise last_exception
    
    async def _wait_before_retry(self, retry_count: int):
        """Wait before retrying with exponential backoff."""
        import asyncio
        wait_time = min(2 ** retry_count, 10)  # Max 10 seconds
        await asyncio.sleep(wait_time)


class ServiceURLs:
    """URLs for all microservices."""
    
    @staticmethod
    def auth_service(endpoint: str = "") -> str:
        """Get Auth Service URL."""
        return f"{settings.AUTH_SERVICE_URL}{endpoint}"
    
    @staticmethod
    def content_service(endpoint: str = "") -> str:
        """Get Content Service URL."""
        return f"{settings.CONTENT_SERVICE_URL}{endpoint}"
    
    @staticmethod
    def partners_crm_service(endpoint: str = "") -> str:
        """Get Partners CRM Service URL."""
        return f"{settings.PARTNERS_CRM_SERVICE_URL}{endpoint}"
    
    @staticmethod
    def projects_service(endpoint: str = "") -> str:
        """Get Projects Service URL."""
        return f"{settings.PROJECTS_SERVICE_URL}{endpoint}"
    
    @staticmethod
    def social_media_service(endpoint: str = "") -> str:
        """Get Social Media Service URL."""
        return f"{settings.SOCIAL_MEDIA_SERVICE_URL}{endpoint}"
    
    @staticmethod
    def notification_service(endpoint: str = "") -> str:
        """Get Notification Service URL."""
        return f"{settings.NOTIFICATION_SERVICE_URL}{endpoint}"


# Singleton instance
service_client = ServiceClient()

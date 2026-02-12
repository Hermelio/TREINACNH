"""
Security middleware for additional protection.
"""
import logging
from django.http import HttpResponseForbidden
from django.core.cache import cache
from django.shortcuts import redirect
from django.urls import resolve

logger = logging.getLogger(__name__)


class StudentRedirectMiddleware:
    """Redirect logged-in students from home/plans to marketplace"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Check if user is authenticated and is a student
        if request.user.is_authenticated:
            if hasattr(request.user, 'profile') and request.user.profile.role == 'STUDENT':
                try:
                    # Get current URL name
                    current_url = resolve(request.path_info).url_name
                    
                    # Redirect from home or plans to cities list (where instructors are shown)
                    if current_url in ['home', 'plans']:
                        return redirect('marketplace:cities_list')
                except:
                    pass
        
        response = self.get_response(request)
        return response


class SecurityMiddleware:
    """
    Custom security middleware for additional protection against attacks.
    """
    
    # Suspicious patterns in user agent
    SUSPICIOUS_USER_AGENTS = [
        'sqlmap', 'nikto', 'nmap', 'masscan', 'nessus', 
        'openvas', 'acunetix', 'appscan', 'burp',
        'metasploit', 'hydra', 'havij', 'pangolin'
    ]
    
    # Suspicious patterns in paths
    SUSPICIOUS_PATHS = [
        'admin/phpMyAdmin', 'wp-admin', 'wp-login',
        '.env', '.git', 'config.php', 'phpinfo',
        '../', '..\\', '%2e%2e', 'eval(', 'base64',
        '<script', 'javascript:', 'onerror='
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Check for suspicious user agents
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        for suspicious in self.SUSPICIOUS_USER_AGENTS:
            if suspicious in user_agent:
                logger.warning(
                    f"Suspicious user agent blocked: {user_agent} "
                    f"from IP: {self.get_client_ip(request)}"
                )
                return HttpResponseForbidden("Access Denied")
        
        # Check for suspicious paths
        path = request.path.lower()
        for suspicious in self.SUSPICIOUS_PATHS:
            if suspicious in path:
                logger.warning(
                    f"Suspicious path blocked: {path} "
                    f"from IP: {self.get_client_ip(request)}"
                )
                return HttpResponseForbidden("Access Denied")
        
        # Check for excessive requests from single IP
        ip = self.get_client_ip(request)
        if self.is_rate_limited(ip):
            logger.warning(f"Rate limit exceeded for IP: {ip}")
            return HttpResponseForbidden("Too Many Requests")
        
        response = self.get_response(request)
        
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'same-origin'
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        return response
    
    def get_client_ip(self, request):
        """Get real client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def is_rate_limited(self, ip):
        """Check if IP has exceeded rate limit"""
        cache_key = f'rate_limit_{ip}'
        requests = cache.get(cache_key, 0)
        
        if requests > 100:  # Max 100 requests per minute
            return True
        
        cache.set(cache_key, requests + 1, 60)  # 60 seconds
        return False

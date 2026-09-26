# authentication.py (or views.py)
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed

class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        # 1. Try to get the token from the HttpOnly cookie
        raw_token = request.COOKIES.get('access_token')
        
        if raw_token is not None:
            try:
                # Validate the token manually
                validated_token = self.get_validated_token(raw_token)
                # Return the user and the validated token
                return self.get_user(validated_token), validated_token
            except Exception as e:
                # If the token is expired or invalid, raise an error
                raise AuthenticationFailed('Invalid or expired token')
        
        # 2. Fallback: If no cookie is found, fall back to the default 
        # Authorization header check (useful for Postman/API clients)
        return super().authenticate(request)
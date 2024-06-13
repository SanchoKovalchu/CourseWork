# Import necessary modules from FastAPI and Starlette
from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from nicegui import Client, app

# Define a set of routes that do not require authentication
unrestricted_page_routes = {'/login'}

class AuthMiddleware(BaseHTTPMiddleware):
    """This middleware restricts access to all pages.
    
    It redirects the user to the login page if they are not authenticated.
    """

    # Override the dispatch method to implement custom middleware behavior
    async def dispatch(self, request: Request, call_next):
        # Check if the user is not authenticated
        if not app.storage.user.get('authenticated', False):
            # If the requested URL is a restricted page and not in the unrestricted routes
            if request.url.path in Client.page_routes.values() and request.url.path not in unrestricted_page_routes:
                # Remember the path the user wanted to access before being redirected
                app.storage.user['referrer_path'] = request.url.path  
                # Redirect the user to the login page
                return RedirectResponse('/login')
        # If the user is authenticated or the page is unrestricted, proceed with the request
        return await call_next(request)

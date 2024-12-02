import os
from flask import url_for, request, current_app

def dated_url_for(endpoint, **values):
    """
    Add version number to static files based on modification time.
    
    This helps in cache busting for static files by appending a timestamp
    to the URL when the file changes.
    """
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(current_app.static_folder, filename)
            if os.path.isfile(file_path):
                values['v'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)

def init_url_versioning(app):
    """
    Initialize URL versioning for static files.
    
    This function should be called in the app factory to set up 
    the context processor for URL versioning.
    """
    @app.context_processor
    def override_url_for():
        return dict(url_for=dated_url_for)


def init_caching(app):
    """
    Initialize caching headers for the application.
    
    This function sets up caching headers to ensure proper 
    caching behavior for static and dynamic content.
    """
    @app.after_request
    def add_header(response):
        """
        Add caching headers to responses.
        
        - Static files are cached for 1 year
        - Other responses are not cached
        """
        if 'static' in request.path:
            # Cache static files for 1 year
            response.headers['Cache-Control'] = 'public, max-age=31536000'
        else:
            # Don't cache other responses
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '-1'
        return response
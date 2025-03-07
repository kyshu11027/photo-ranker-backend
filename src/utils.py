import os

def get_cors_headers(event):
    # Get the origin from the request
    origin = event.get('headers', {}).get('origin') or event.get('headers', {}).get('Origin')
    
    # Set allowed origins based on environment
    workspace = os.environ.get('TERRAFORM_WORKSPACE', 'dev')
    allowed_origins = ["https://pickpix.vercel.app"]
    if workspace == 'dev':
        allowed_origins.append("http://localhost:3000")
    
    # Use the requesting origin if it's allowed, otherwise use default
    cors_origin = origin if origin in allowed_origins else allowed_origins[0]
    
    return {
        "Access-Control-Allow-Origin": cors_origin,
        "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
        "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
        "Access-Control-Allow-Credentials": "true"
    }
import os
import jwt
import requests

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

def get_public_key(auth0_domain):
    jwks_url = f"https://{auth0_domain}/.well-known/jwks.json"
    try:
        response = requests.get(jwks_url, timeout=5)
        response.raise_for_status()
        jwks = response.json()

        if "keys" not in jwks or not jwks["keys"]:
            raise ValueError("No public keys found in JWKS response")

        return jwks["keys"][0]

    except requests.RequestException as e:
        print(f"Error fetching JWKS: {e}")
        raise

    except (ValueError, KeyError) as e:
        print(f"Error processing JWKS: {e}")
        raise

def extract_token(event):
    auth_header = event.get("headers", {}).get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        raise ValueError("Missing or invalid Authorization header")
    return auth_header.split(" ")[1]

def verify_token(event, auth0_domain, api_audience, expected_issuer):
    token = extract_token(event)
    public_key = get_public_key(auth0_domain)
    try:
        payload = jwt.verify(
            token, 
            public_key, 
            algorithms=["RS256"], 
            audience=api_audience, 
            iss=expected_issuer
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise Exception("Token expired")
    except jwt.InvalidAudienceError:
        raise Exception("Invalid audience")
    except jwt.InvalidIssuerError:
        raise Exception("Invalid Issuer")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token")

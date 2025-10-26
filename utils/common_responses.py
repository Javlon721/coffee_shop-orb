authorization_header = {
  "parameters": [
    {
      "name": "Authorization",
      "in": "header",
      "required": True,
      "schema": {"type": "string"},
      "description": "String with access_token bearer",
      "example": "Bearer access_token_here"
    }
  ]
}

token_responses = {
  "400": {
    "description": "Access token expired error",
    "content": {
      "application/json": {
        "example": {"detail": "Access token expired"}
      }
    }
  },
  "401": {
    "description": "Invalid user credentials error",
    "content": {
      "application/json": {
        "example": {"detail": "Could not validate credentials"}
      }
    }
  },
}
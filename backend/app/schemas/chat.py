"""
Chat API Schemas and Models
Pydantic models for request and response validation
"""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """
    Chat request model
    
    Attributes:
        message: The user's message to the AI agent (required, non-empty)
    """
    
    message: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="User message to send to the AI agent",
        example="Hello, how are you?"
    )
    
    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "message": "What is the weather today?"
            }
        }


class ChatResponse(BaseModel):
    """
    Chat response model
    
    Attributes:
        response: The AI agent's response to the user
    """
    
    response: str = Field(
        description="Response from the Personal AI Agent",
        example="This is a response from the Personal AI Agent"
    )
    
    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "response": "This is a dummy response from the Personal AI Agent."
            }
        }

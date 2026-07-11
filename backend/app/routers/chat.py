"""
Chat Router
Endpoints for chat interactions with the Personal AI Agent
"""

import json
from typing import Generator

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.gemini_service import gemini_service


# Create router instance
router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
    responses={
        400: {"description": "Bad request - Invalid message"},
        500: {"description": "Internal server error"},
    }
)


@router.post(
    "",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Send a message to the AI Agent",
    description="Send a message to the Personal AI Agent and receive a response",
)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Send a message to the Personal AI Agent using Google Gemini
    
    Args:
        request: ChatRequest model containing the user's message
        
    Returns:
        ChatResponse: Contains the AI agent's response
        
    Raises:
        HTTPException: 400 if message is invalid
        HTTPException: 500 if Gemini API fails
        HTTPException: 503 if service is unavailable
    """
    
    # Validate message is not empty (Pydantic already validates min_length)
    if not request.message or not request.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty or contain only whitespace"
        )
    
    try:
        # Call Gemini service to generate response
        ai_response = gemini_service.generate_response(request.message)
        
        return ChatResponse(response=ai_response)
    
    except ValueError as e:
        # Handle validation and configuration errors
        detail = str(e)
        
        # Check for specific error types
        if "GEMINI_API_KEY" in detail or "not configured" in detail:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI service is not properly configured. "
                       "Please contact support."
            )
        elif "authentication" in detail.lower():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI service authentication failed. "
                       "Please contact support."
            )
        elif "quota" in detail.lower():
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="API quota exceeded. Please try again later."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=detail
            )
    
    except Exception as e:
        # Handle unexpected errors
        detail = f"AI service error: {str(e)}"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request. "
                   "Please try again later."
        )


@router.post(
    "/stream",
    response_class=StreamingResponse,
    status_code=status.HTTP_200_OK,
    summary="Stream AI responses in real-time",
    description="Stream message responses progressively using Server-Sent Events (SSE), similar to ChatGPT",
)
async def chat_stream(request: ChatRequest):
    """
    Stream a message to the Personal AI Agent using real-time token streaming.
    
    The response is streamed using Server-Sent Events (SSE) format,
    allowing progressive delivery of tokens from the Gemini model as they are generated.
    
    Args:
        request: ChatRequest model containing the user's message.
        
    Returns:
        StreamingResponse: SSE stream with format "data: {token}\n\n" for each token.
        
    Raises:
        HTTPException: Various status codes based on error type (400, 429, 503, 500).
        
    Example frontend usage (JavaScript):
        const eventSource = new EventSource('/chat/stream');
        eventSource.onmessage = (event) => {
            const token = event.data;
            console.log('Received token:', token);
        };
        eventSource.onerror = () => eventSource.close();
    """
    
    # ========== INPUT VALIDATION ==========
    if not request.message or not request.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty or contain only whitespace"
        )

    # ========== GENERATOR FUNCTION FOR STREAMING ==========
    def stream_generator() -> Generator[str, None, None]:
        """
        Generator that yields SSE-formatted tokens from the Gemini service.
        
        SSE format: "data: {content}\n\n"
        - Each event is JSON-encoded for safe transmission
        - Empty lines (\n\n) delimit events
        - Frontend parses with EventSource API
        """
        try:
            # Call the streaming service which yields tokens as they arrive
            for token in gemini_service.stream_response(request.message):
                # Package token as SSE event
                # Format: "data: {json_string}\n\n"
                event_data = json.dumps({"token": token, "type": "chunk"})
                yield f"data: {event_data}\n\n"

        except ValueError as e:
            # Handle service-level validation/config errors
            error_detail = str(e)
            
            # Send error event to client before closing stream
            if "GEMINI_API_KEY" in error_detail or "not configured" in error_detail:
                error_msg = "AI service is not properly configured."
                error_code = "SERVICE_NOT_CONFIGURED"
            elif "authentication" in error_detail.lower():
                error_msg = "AI service authentication failed."
                error_code = "AUTH_FAILED"
            elif "quota" in error_detail.lower():
                error_msg = "API quota exceeded. Please try again later."
                error_code = "QUOTA_EXCEEDED"
            else:
                error_msg = error_detail
                error_code = "SERVICE_ERROR"

            # Yield final error event
            error_event = json.dumps({
                "type": "error",
                "code": error_code,
                "message": error_msg
            })
            yield f"data: {error_event}\n\n"

        except Exception as e:
            # Catch unexpected errors during streaming
            error_event = json.dumps({
                "type": "error",
                "code": "UNKNOWN_ERROR",
                "message": "An unexpected error occurred during streaming."
            })
            yield f"data: {error_event}\n\n"

        finally:
            # Send completion event to signal stream end
            completion_event = json.dumps({
                "type": "complete",
                "message": "Stream ended"
            })
            yield f"data: {completion_event}\n\n"

    # ========== RETURN STREAMING RESPONSE ==========
    # StreamingResponse will:
    # 1. Set Content-Type to text/event-stream
    # 2. Keep the connection open
    # 3. Send events as they are yielded by the generator
    # 4. Close connection when generator completes
    return StreamingResponse(
        stream_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable buffering on nginx
        }
    )


"""
Google Gemini AI Service
Handles integration with Google Gemini API for AI-powered responses
"""

import logging
from typing import Optional

try:
    from google import genai
except ImportError:
    genai = None

from app.core.config import get_settings

# Configure logging
logger = logging.getLogger(__name__)


class GeminiService:
    """
    Service for interacting with Google Gemini API
    Handles API initialization, request handling, and error management
    """

    def __init__(self):
        """Initialize Gemini service with configuration from environment"""
        self.settings = get_settings()
        self.api_key = self.settings.GEMINI_API_KEY
        self.model_name = self.settings.GEMINI_MODEL
        self.client: Optional[object] = None

    def _validate_api_key(self) -> None:
        """
        Validate that the Gemini API key is configured.

        Raises:
            ValueError: If the API key is not configured.
        """
        if not self.api_key or not self.api_key.strip():
            logger.error("GEMINI_API_KEY is not set in environment variables")
            raise ValueError(
                "GEMINI_API_KEY is not configured. "
                "Please set the GEMINI_API_KEY environment variable."
            )

    def _initialize_client(self) -> None:
        """
        Initialize the Google Gemini client.

        Raises:
            ValueError: If the API key is missing.
            ImportError: If google-genai is not installed.
            ValueError: If client initialization fails.
        """
        if self.client is not None:
            return

        self._validate_api_key()

        if genai is None:
            logger.error("google-genai package is not installed")
            raise ImportError(
                "google-genai package is required for Gemini integration. "
                "Install it with: pip install google-genai"
            )

        try:
            self.client = genai.Client(api_key=self.api_key)
            logger.info(f"Gemini client initialized with model: {self.model_name}")
        except TypeError as exc:
            logger.error(f"Invalid Gemini client configuration: {exc}")
            raise ValueError(
                "Failed to initialize Gemini client. "
                "Please validate GEMINI_API_KEY and gemini settings."
            )
        except Exception as exc:
            logger.error(f"Failed to initialize Gemini client: {exc}")
            raise ValueError(
                f"Failed to initialize Gemini service: {exc}"
            )

    def _extract_text(self, response) -> str:
        """
        Extract text from a Gemini generate_content response.

        Args:
            response: The raw response object from Gemini.

        Returns:
            str: The extracted response text.
        """
        # Log response structure for comprehensive debugging
        logger.info(f"Response type: {type(response).__name__}")
        logger.info(f"Response attributes: {[x for x in dir(response) if not x.startswith('_')][:25]}")

        # Try direct .text attribute (some SDK versions)
        text_value = getattr(response, "text", None)
        if text_value:
            logger.info("✓ Extracted text from response.text")
            return text_value

        # Try candidates[0].content.parts[0].text (typical latest Gemini SDK)
        candidates = getattr(response, "candidates", None)
        if candidates and len(candidates) > 0:
            logger.info(f"✓ Found {len(candidates)} candidate(s)")
            candidate = candidates[0]
            logger.info(f"  Candidate type: {type(candidate).__name__}")

            content = getattr(candidate, "content", None)
            if content:
                logger.info(f"  ✓ Found content: {type(content).__name__}")
                parts = getattr(content, "parts", None)
                if parts:
                    logger.info(f"    ✓ Found {len(parts)} part(s)")
                    text_segments = []
                    for i, part in enumerate(parts):
                        logger.info(f"      Part {i}: {type(part).__name__}")
                        part_text = getattr(part, "text", None)
                        if part_text:
                            logger.info(f"      ✓ Extracted from part {i}: {part_text[:80]}")
                            text_segments.append(part_text)
                    text = "".join(text_segments).strip()
                    if text:
                        return text

        # Fallback: try response.parts
        parts = getattr(response, "parts", None)
        if parts:
            logger.info(f"✓ Found {len(parts)} part(s) on response.parts")
            text_segments = []
            for part in parts:
                part_text = getattr(part, "text", None)
                if part_text:
                    text_segments.append(part_text)
            text = "".join(text_segments).strip()
            if text:
                return text

        # Log the entire response as string for final debugging
        logger.error(f"✗ No text extracted. Full response: {repr(response)}")
        raise ValueError(
            "Received empty response from Gemini API. "
            "The API may have rejected your input."
        )

    def generate_response(self, message: str) -> str:
        """
        Generate an AI response using Google Gemini.

        Args:
            message: The user's input message.

        Returns:
            str: The AI-generated response.

        Raises:
            ValueError: If validation fails or the response is empty.
        """
        if not message or not message.strip():
            raise ValueError("Message cannot be empty or contain only whitespace")

        self._initialize_client()

        # Configuration for retries on transient 503 errors
        max_retries = 3
        backoff_base = 0.5  # seconds

        # Fallback message if Gemini returns nothing
        fallback_message = (
            "I'm sorry — I couldn't generate a response right now. Please try again in a moment."
        )

        # Retry loop for transient failures (503, network errors)
        for attempt in range(max_retries):
            try:
                logger.info(f"Sending request to Gemini model: {self.model_name} (attempt {attempt + 1})")
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=message,
                )

                # Log raw response for debugging
                try:
                    if hasattr(response, "model_dump"):
                        logger.debug("Raw Gemini response: %s", response.model_dump())
                    else:
                        logger.debug("Raw Gemini response repr: %s", repr(response))
                except Exception:
                    logger.debug("Failed to log raw Gemini response")

                # Try to extract text; return fallback if empty
                try:
                    text = self._extract_text(response)
                    if not text:
                        logger.warning("Gemini returned empty text; returning fallback message")
                        return fallback_message
                    return text
                except ValueError as e:
                    logger.warning("Gemini returned no usable content: %s", str(e))
                    return fallback_message

            except Exception as exc:
                error_message = str(exc)
                lower_msg = error_message.lower()
                logger.warning(f"Gemini call failed (model={self.model_name}, attempt {attempt + 1}): {error_message}")

                # Handle service unavailable (503) with retries + exponential backoff
                if "503" in lower_msg or "service unavailable" in lower_msg or "server error" in lower_msg:
                    if attempt < max_retries - 1:
                        sleep_time = backoff_base * (2 ** attempt)
                        logger.info(f"Retrying after {sleep_time}s due to 503/Server error")
                        import time
                        time.sleep(sleep_time)
                        continue
                    else:
                        raise ValueError("AI service is temporarily unavailable. Please try again later.")

                # Map common errors to friendly messages
                if "401" in lower_msg or "authentication" in lower_msg:
                    raise ValueError(
                        "Authentication failed. Please verify your GEMINI_API_KEY is valid."
                    )
                if "429" in lower_msg or "quota" in lower_msg:
                    raise ValueError(
                        "API quota exceeded. Please try again later."
                    )
                if "network" in lower_msg or "connection" in lower_msg:
                    raise ValueError(
                        "Network error occurred. Please check your internet connection."
                    )

                # Unknown error: surface message
                raise ValueError(f"Gemini API error: {error_message}")

        # If all attempts exhausted without success, return fallback
        logger.warning("All Gemini attempts exhausted; returning fallback message")
        return fallback_message

    def stream_response(self, message: str):
        """
        Stream an AI response from Google Gemini using Server-Sent Events (SSE).

        Yields tokens progressively as they are generated by the model.
        This enables real-time, ChatGPT-like streaming responses.

        Args:
            message: The user's input message.

        Yields:
            str: Text chunks as they are streamed from the Gemini API.

        Raises:
            ValueError: If the message is invalid or authentication fails.
        """
        if not message or not message.strip():
            raise ValueError("Message cannot be empty or contain only whitespace")

        self._initialize_client()

        try:
            logger.info(f"Starting stream to Gemini model: {self.model_name}")

            # Call generate_content_stream to get a streaming response
            # This returns an iterator of response chunks as they arrive from the API
            # Each chunk contains partial text that can be sent to the client immediately
            stream = self.client.models.generate_content_stream(
                model=self.model_name,
                contents=message,
            )

            # Iterate over chunks as they arrive from the API
            # Each chunk contains partial text that can be sent to the client immediately
            for chunk in stream:
                try:
                    # Extract text from the chunk
                    text = self._extract_chunk_text(chunk)
                    if text:
                        # Yield the token for SSE transmission
                        # The router will format this as "data: {json}\n\n"
                        logger.debug(f"Streaming chunk: {text[:50]}")
                        yield text
                except Exception as chunk_error:
                    logger.error(f"Error processing chunk: {chunk_error}")
                    # Send readable error message to frontend
                    yield f"Error processing response: {str(chunk_error)}"

            logger.info("Stream completed successfully")

        except Exception as exc:
            error_message = str(exc)
            lower_msg = error_message.lower()
            logger.error(f"Streaming failed (model={self.model_name}): {error_message}")

            # Map common errors to user-friendly messages
            if "401" in lower_msg or "authentication" in lower_msg:
                raise ValueError(
                    "Authentication failed. Please verify your GEMINI_API_KEY is valid."
                )
            if "429" in lower_msg or "quota" in lower_msg:
                raise ValueError(
                    "API quota exceeded. Please try again later."
                )
            if "network" in lower_msg or "connection" in lower_msg:
                raise ValueError(
                    "Network error occurred. Please check your internet connection."
                )

            # Re-raise with context
            raise ValueError(f"Streaming error: {error_message}")

    def _extract_chunk_text(self, chunk) -> str:
        """
        Extract text from a streaming chunk returned by Gemini.

        In streaming mode, chunks have a simpler structure than full responses.
        Usually contains: chunk.text or chunk.candidates[0].content.parts[0].text

        Args:
            chunk: The chunk object from the stream.

        Returns:
            str: The extracted text, or empty string if no text in chunk.
        """
        # Try direct .text attribute first (most common in streaming)
        if hasattr(chunk, "text") and chunk.text:
            return chunk.text

        # Fallback: try candidates structure
        try:
            candidates = getattr(chunk, "candidates", None)
            if candidates and len(candidates) > 0:
                content = getattr(candidates[0], "content", None)
                if content:
                    parts = getattr(content, "parts", None)
                    if parts and len(parts) > 0:
                        part_text = getattr(parts[0], "text", None)
                        if part_text:
                            return part_text
        except Exception:
            pass

        # No text in this chunk (might be metadata-only chunk)
        return ""


# ========== SINGLETON INSTANCE ==========
# Create a single instance of GeminiService to be used throughout the application
# This instance is initialized once and reused for all requests
gemini_service = GeminiService()

"""
HuggingFace Inference API Adapter
Implements BaseModelAdapter for HuggingFace models (Mistral, Llama, etc.)
Uses the HuggingFace Inference API for fast, unlimited requests
"""

import time
import asyncio
from typing import Optional, List, AsyncIterator, Dict, Any
import aiohttp
from adapters.base import (
    BaseModelAdapter,
    ModelResponse,
    ConversationMessage,
    AdapterInitializationError,
    AdapterRequestError,
    AdapterTimeoutError,
    AdapterRateLimitError
)


class HuggingFaceAdapter(BaseModelAdapter):
    """Adapter for HuggingFace Inference API (unlimited requests)"""
    
    DEFAULT_ENDPOINT = "https://api-inference.huggingface.co/models"
    
    async def initialize(self) -> None:
        """Initialize the HTTP client session"""
        if not self.config.api_key:
            raise AdapterInitializationError(
                "HuggingFace API key is required. Set HF_API_KEY environment variable or pass it in config."
            )
        
        timeout = aiohttp.ClientTimeout(total=self.config.timeout)
        self._client = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            },
            timeout=timeout
        )
        self._initialized = True
    
    def _build_prompt(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        conversation_history: Optional[List[ConversationMessage]] = None
    ) -> str:
        """
        Build conversation prompt in Mistral chat format
        Mistral format: [INST] instruction [/INST] response </s>[INST] next [/INST]
        """
        full_prompt = ""
        
        # Add system prompt if provided
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n"
        
        # Add conversation history
        if conversation_history:
            for msg in conversation_history:
                if msg.role == "user":
                    full_prompt += f"[INST] {msg.content} [/INST]"
                else:  # assistant
                    full_prompt += f" {msg.content} </s>"
        
        # Add current prompt
        if conversation_history:
            # If we have history, start a new conversation turn
            full_prompt += f"[INST] {prompt} [/INST]"
        else:
            # If no history, just use the instruction format
            full_prompt = f"{full_prompt}[INST] {prompt} [/INST]"
        
        return full_prompt
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        conversation_history: Optional[List[ConversationMessage]] = None,
        **kwargs
    ) -> ModelResponse:
        """Generate response from HuggingFace Inference API"""
        
        if not self.is_initialized:
            await self.initialize()
        
        # Build the full prompt
        full_prompt = self._build_prompt(prompt, system_prompt, conversation_history)
        
        # Merge parameters
        params = self._merge_parameters(kwargs)
        
        # Build request payload optimized for Mistral
        payload = {
            "inputs": full_prompt,
            "parameters": {
                "max_new_tokens": params.get("max_tokens", 500),
                "temperature": params.get("temperature", 0.7),
                "top_p": params.get("top_p", 0.95),
                "do_sample": True,
                "repetition_penalty": 1.1,  # Prevent repetition
            },
            "details": True,  # Get detailed output
        }
        
        # Build endpoint URL
        model_id = self.config.model_name or "mistralai/Mistral-7B-Instruct-v0.2"
        endpoint = f"{self.DEFAULT_ENDPOINT}/{model_id}"
        
        last_error: Optional[Exception] = None
        
        for attempt in range(self.config.max_retries):
            try:
                start_time = time.time()
                
                async with self._client.post(endpoint, json=payload) as response:
                    latency_ms = int((time.time() - start_time) * 1000)
                    
                    # Try to parse as JSON
                    try:
                        response_data = await response.json()
                    except Exception:
                        # Not JSON, get text instead
                        response_text = await response.text()
                        if response.status != 200:
                            raise AdapterRequestError(
                                f"HuggingFace API error ({response.status}): {response_text[:500]}\n"
                                f"Make sure you have the correct HF_API_KEY and the model is accessible."
                            )
                        response_data = response_text
                    
                    # Handle API errors
                    if response.status == 429:
                        # Rate limit
                        wait_time = 2 ** attempt
                        print(f"\n   ⏳ HuggingFace rate limited. Waiting {wait_time}s before retry {attempt + 1}/{self.config.max_retries}...")
                        last_error = AdapterRateLimitError("HuggingFace API rate limited")
                        await asyncio.sleep(wait_time)
                        continue
                    
                    if response.status == 503:
                        # Model is loading
                        wait_time = 10 + (2 ** attempt)
                        print(f"\n   ⏳ Model loading. Waiting {wait_time}s before retry {attempt + 1}/{self.config.max_retries}...")
                        last_error = AdapterRequestError("Model is loading, please retry")
                        await asyncio.sleep(wait_time)
                        continue
                    
                    if response.status != 200:
                        error_msg = response_data.get("error", "Unknown error") if isinstance(response_data, dict) else str(response_data)
                        raise AdapterRequestError(f"HuggingFace API error ({response.status}): {error_msg}")
                    
                    # Parse response
                    # HuggingFace returns array of generated sequences
                    if isinstance(response_data, list) and len(response_data) > 0:
                        result = response_data[0]
                    else:
                        result = response_data
                    
                    # Extract generated text
                    generated_text = result.get("generated_text", "")
                    
                    # Clean up the response - remove the prompt from the output if it's included
                    if full_prompt in generated_text:
                        generated_text = generated_text.replace(full_prompt, "", 1).strip()
                    
                    # Extract closing tag if present in Mistral format
                    if "</s>" in generated_text:
                        generated_text = generated_text.split("</s>")[0].strip()
                    
                    return ModelResponse(
                        content=generated_text,
                        model=self.config.model_name or "mistralai/Mistral-7B-Instruct-v0.2",
                        finish_reason=result.get("finish_reason", "length"),
                        tokens_used=result.get("details", {}).get("generated_tokens", 0),
                        latency_ms=latency_ms,
                        raw_response=response_data,
                        metadata={
                            "generation_time": result.get("details", {}).get("generation_time", 0),
                        }
                    )
                    
            except asyncio.TimeoutError:
                last_error = AdapterTimeoutError(f"HuggingFace request timed out after {self.config.timeout}s")
                if attempt < self.config.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                else:
                    raise last_error
            
            except Exception as e:
                if isinstance(e, (AdapterRequestError, AdapterRateLimitError, AdapterTimeoutError)):
                    raise
                last_error = AdapterRequestError(f"HuggingFace request failed: {str(e)}")
                if attempt < self.config.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                else:
                    raise last_error
        
        # All retries exhausted
        if last_error:
            raise last_error
        raise AdapterRequestError("HuggingFace request failed after all retries")
    
    async def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        conversation_history: Optional[List[ConversationMessage]] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Generate streaming response from HuggingFace API
        Note: HuggingFace free tier doesn't support streaming for some models,
        so we'll return chunks of the full response
        """
        response = await self.generate(prompt, system_prompt, conversation_history, **kwargs)
        
        # Yield the response in chunks for compatibility
        chunk_size = 50
        for i in range(0, len(response.content), chunk_size):
            yield response.content[i:i+chunk_size]
    
    async def health_check(self) -> bool:
        """Check if HuggingFace API is accessible"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            # Test with a simple request
            test_payload = {
                "inputs": "[INST] Hello [/INST]",
                "parameters": {
                    "max_new_tokens": 10,
                },
                "details": True,
            }
            
            model_id = self.config.model_name or "mistralai/Mistral-7B-Instruct-v0.2"
            endpoint = f"{self.DEFAULT_ENDPOINT}/{model_id}"
            
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(
                headers={
                    "Authorization": f"Bearer {self.config.api_key}",
                    "Content-Type": "application/json"
                },
                timeout=timeout
            ) as session:
                async with session.post(endpoint, json=test_payload) as response:
                    return response.status == 200
        
        except Exception as e:
            print(f"Health check failed: {e}")
            return False
    
    async def close(self) -> None:
        """Close the HTTP client session"""
        if self._client:
            await self._client.close()

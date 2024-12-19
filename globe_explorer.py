from typing import Optional, List, Dict, Any, Union
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
import json
import uuid
import requests
from requests.exceptions import RequestException

class GlobeExplorerError(Exception):
    """Base exception class for Globe Explorer related errors."""
    pass

class ModelNotFoundError(GlobeExplorerError):
    """Raised when an invalid model is specified."""
    pass

class APIConnectionError(GlobeExplorerError):
    """Raised when there's an error connecting to the Globe Explorer API."""
    pass

class ResponseProcessingError(GlobeExplorerError):
    """Raised when there's an error processing the API response."""
    pass

class ModelType(Enum):
    """Enumeration of available Globe Explorer models."""
    DEFAULT = "default"
    TURBO = "turbo"
    
    @classmethod
    def from_string(cls, model_name: str) -> 'ModelType':
        """Convert string model name to ModelType enum."""
        try:
            return cls[model_name.upper()]
        except KeyError:
            raise ModelNotFoundError(
                f"Invalid model '{model_name}'. Available models: {', '.join(m.name for m in cls)}"
            )

@dataclass
class SearchQuery:
    """Data class representing a search query."""
    query: str
    search_id: str = str(uuid.uuid1())
    index: int = 0
    type: str = "initial_searchbox"
    clicked_category: Optional[str] = None
    staged_image: Optional[str] = None
    location: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert the search query to a dictionary format."""
        return {
            "searchbox_query": self.query,
            "search_id": self.search_id,
            "index": self.index,
            "type": self.type,
            "clicked_category": self.clicked_category,
            "staged_image": self.staged_image,
            "location": self.location
        }

@dataclass
class APIResponse:
    """Data class representing the API response."""
    streaming_response: str = ""
    images: List[Dict[str, Any]] = None
    error: Optional[str] = None

    def __post_init__(self):
        """Initialize default values after dataclass initialization."""
        if self.images is None:
            self.images = []

class ResponseProcessor(ABC):
    """Abstract base class for response processors."""
    
    @abstractmethod
    def process_line(self, line: str, response: APIResponse, prints: bool) -> None:
        """Process a single line of the streaming response."""
        pass

class JSONResponseProcessor(ResponseProcessor):
    """Concrete implementation of response processor for JSON data."""
    
    def process_line(self, line: str, response: APIResponse, prints: bool) -> None:
        """Process a single line of JSON response data."""
        try:
            line = line.replace("data: ", "")
            json_value = json.loads(line)
            
            if json_value['type'] == 'top_answer_chunk':
                content = json_value['data']
                if prints:
                    print(content, end="", flush=True)
                response.streaming_response += content
            elif json_value['type'] == 'image':
                response.images.append(json_value['data'])
                
        except json.JSONDecodeError as e:
            raise ResponseProcessingError(f"Failed to decode JSON response: {str(e)}")
        except KeyError as e:
            raise ResponseProcessingError(f"Missing required key in response: {str(e)}")

class GlobeExplorerClient:
    """
    A professional client for interacting with the Globe Explorer AI API.
    
    This client provides a robust interface for making queries to the Globe Explorer
    API with proper error handling and type safety.
    """
    
    BASE_URL = "https://explorer-search.fly.dev/submitSearch"
    
    def __init__(self, response_processor: Optional[ResponseProcessor] = None):
        """
        Initialize the Globe Explorer client.
        
        Args:
            response_processor: Custom response processor implementation.
                              Defaults to JSONResponseProcessor if None.
        """
        self.headers = {
            'accept': 'text/event-stream',
            'accept-language': 'en-US,en;q=0.6',
            'cache-control': 'no-cache',
            'origin': 'https://explorer.globe.engineer',
            'priority': 'u=1, i',
            'referer': 'https://explorer.globe.engineer/',
            'sec-ch-ua': '"Brave";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'sec-gpc': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        }
        self.response_processor = response_processor or JSONResponseProcessor()

    def query(
        self,
        query: str,
        model: Union[str, ModelType] = ModelType.DEFAULT,
        prints: bool = True
    ) -> APIResponse:
        """
        Execute a query against the Globe Explorer AI.
        
        Args:
            query: The search query to send to Globe Explorer
            model: The model to use for the query (ModelType enum or string)
            prints: Whether to print streaming responses in real-time
            
        Returns:
            APIResponse object containing the response data
            
        Raises:
            ModelNotFoundError: If an invalid model is specified
            APIConnectionError: If there's an error connecting to the API
            ResponseProcessingError: If there's an error processing the response
        """
        if isinstance(model, str):
            model = ModelType.from_string(model)
            
        params = self._build_params(query, model)
        
        try:
            response = requests.get(
                self.BASE_URL,
                params=params,
                headers=self.headers,
                stream=True,
                timeout=None
            )
            response.raise_for_status()
            
            return self._process_response(response, prints)
            
        except RequestException as e:
            raise APIConnectionError(f"Failed to connect to API: {str(e)}")

    def _build_params(self, query: str, model: ModelType) -> Dict[str, str]:
        """
        Build the request parameters for the API call.
        
        Args:
            query: The search query
            model: The ModelType enum value
            
        Returns:
            Dictionary of request parameters
        """
        search_query = SearchQuery(query=query)
        
        return {
            'queryData': json.dumps([search_query.to_dict()]),
            'userid_auth': 'undefined',
            'userid_local': f"user_{uuid.uuid4().hex}_g0sdqrryy",
            'model': model.value,
            'search_id': uuid.uuid4().hex,
        }

    def _process_response(self, response: requests.Response, prints: bool) -> APIResponse:
        """
        Process the streaming response from the API.
        
        Args:
            response: The requests.Response object
            prints: Whether to print streaming responses
            
        Returns:
            APIResponse object containing processed data
            
        Raises:
            ResponseProcessingError: If there's an error processing the response
        """
        api_response = APIResponse()
        
        try:
            for line in response.iter_lines(decode_unicode=True, chunk_size=1000):
                if line:
                    self.response_processor.process_line(line, api_response, prints)
            return api_response
            
        except Exception as e:
            raise ResponseProcessingError(f"Failed to process response: {str(e)}")

# Example usage
if __name__ == "__main__":
    try:
        client = GlobeExplorerClient()
        response = client.query("what is the current AQI in New Delhi")
        
        print(f"\nStreaming Response: {response.streaming_response}\n")
        
        for image_data in response.images:
            print(f"Path: {image_data.get('path', 'N/A')}\n")
            
            for image in image_data.get("images", []):
                if thumbnail_url := image.get('thumbnailUrl'):
                    if thumbnail_url not in ["/loading_image.gif", None]:
                        print(f"Thumbnail URL: {thumbnail_url}")
                        
                if image_url := image.get('imageUrl'):
                    if image_url not in ["/loading_image.gif", None]:
                        print(f"Image URL: {image_url}")
                        
                if link := image.get('link'):
                    print(f"Link: {link}")
                    
                if path := image.get('path'):
                    print(f"Path: {path}")
                    
                if search_query := image.get('imageSearchQuery'):
                    print(f"Image Search Query: {search_query}\n")
                    
    except GlobeExplorerError as e:
        print(f"Error: {str(e)}")
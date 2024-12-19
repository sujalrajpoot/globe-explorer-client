# Globe Explorer AI Client

## 🌟 Overview
The Globe Explorer AI Client is a Python library that provides a robust and type-safe interface for interacting with the Globe Explorer search platform. This client implements professional-grade Object-Oriented Programming patterns and modern Python features to ensure reliability, maintainability, and ease of use.

## ⚠️ Disclaimer
This code is provided strictly for **educational purposes** only. It is designed to demonstrate modern Python programming practices, design patterns, and API interaction techniques. The use of this code to harm, disrupt, or disrespect Globe Explorer's services or infrastructure is strictly prohibited. Users should:
- Respect Globe Explorer's terms of service and API limitations
- Not use this code for automated scraping or excessive querying
- Consider obtaining official API access for production use
- Use this code only for learning and understanding API interactions

## 🎯 Features
- Type-safe interaction with Globe Explorer's search API
- Robust error handling with custom exception hierarchy
- Streaming response processing with real-time output
- Support for multiple model types (Default and Turbo)
- Extensible response processing system
- Comprehensive documentation and type hints
- Image data extraction and processing

## 🛠️ Installation
```bash
# Clone the repository
git clone https://github.com/sujalrajpoot/globe-explorer-client.git

# Navigate to the project directory
cd globe-explorer-client

# Install required dependencies
pip install requests
```

## 📋 Requirements
- Python 3.8+
- requests
- dataclasses (included in Python 3.7+)
- typing-extensions (for Python <3.8)

## 🚀 Quick Start
```python
from globe_explorer import GlobeExplorerClient, GlobeExplorerError

# Create a client instance
client = GlobeExplorerClient()

try:
    # Make a simple query
    response = client.query("what is the current AQI in New Delhi")
    
    # Print the response
    print(f"Response: {response.streaming_response}")
    
    # Process images if available
    for image in response.images:
        print(f"Image URL: {image.get('imageUrl')}")
        
except GlobeExplorerError as e:
    print(f"Error occurred: {str(e)}")
```

## 🔧 Advanced Usage

### Custom Response Processing
```python
from globe_explorer import ResponseProcessor, APIResponse

class CustomResponseProcessor(ResponseProcessor):
    def process_line(self, line: str, response: APIResponse, prints: bool) -> None:
        # Custom processing logic here
        pass

# Use custom processor
client = GlobeExplorerClient(response_processor=CustomResponseProcessor())
```

### Using Different Models
```python
from globe_explorer import ModelType

# Using enum
response = client.query("your query", model=ModelType.TURBO)

# Using string
response = client.query("your query", model="TURBO")
```

## 🏗️ Architecture

### Class Hierarchy
```
GlobeExplorerError
├── ModelNotFoundError
├── APIConnectionError
└── ResponseProcessingError

ResponseProcessor (ABC)
└── JSONResponseProcessor

DataClasses
├── SearchQuery
└── APIResponse

Enums
└── ModelType
```

### Key Components
- **GlobeExplorerClient**: Main client class for API interaction
- **ResponseProcessor**: Abstract base class for response processing
- **ModelType**: Enum class for available models
- **SearchQuery**: Data class for structuring queries
- **APIResponse**: Data class for organizing responses

## 🌟 Best Practices
When using this client, consider the following best practices:

1. **Error Handling**
```python
try:
    response = client.query("your query")
except ModelNotFoundError as e:
    # Handle invalid model
    pass
except APIConnectionError as e:
    # Handle connection issues
    pass
except ResponseProcessingError as e:
    # Handle processing errors
    pass
except GlobeExplorerError as e:
    # Handle other errors
    pass
```

2. **Resource Management**
```python
# Use context managers when extending the client
with GlobeExplorerClient() as client:
    response = client.query("your query")
```

## 🤔 FAQ

**Q: Is this an official Globe Explorer client?**
A: No, this is an unofficial client created for educational purposes.

**Q: Can I use this in production?**
A: This code is for educational purposes only. For production use, please refer to Globe Explorer's official API documentation.

**Q: How can I handle rate limiting?**
A: Currently, rate limiting is not implemented. It's recommended to implement your own rate limiting logic or wait for future updates.

## 📞 Support
For questions, issues, or suggestions:
1. Open an issue in the repository
2. Join our Discord community (coming soon)
3. Check the FAQ section

## 🙏 Acknowledgments
- Globe Explorer for their amazing service
- The Python community for inspiration
- All contributors who help improve this project

Remember to respect Globe Explorer's terms of service and use this client responsibly!

- Thanks to all contributors who have helped with code and documentation
- Special thanks to the Python community for providing excellent tools and libraries

## License

[MIT](https://choosealicense.com/licenses/mit/)

## Contact
For questions or support, please open an issue or reach out to the maintainer.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

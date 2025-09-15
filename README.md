# Social Companionship API

A FastAPI server that provides top news stories and audiobook functionality for the Social Companionship Agent, specifically designed for ElevenLabs integration.

## Features

### News API
- **Top News Stories**: Get current top news stories filtered for positive, senior-friendly content
- **Multi-language Support**: Spanish and English content
- **Category Filtering**: Support for various news categories (general, sports, culture, etc.)
- **Positive Content Filtering**: Automatically filters out negative content suitable for seniors

### Audiobook API
- **LibriVox Integration**: Access to thousands of free audiobooks
- **Search Functionality**: Search by title, author, or genre
- **Audio Playback**: Get audio URLs for audiobook playback
- **Comprehensive Metadata**: Book details, duration, chapters, and more

### General Features
- **RESTful API**: Simple HTTP endpoints for easy integration
- **Comprehensive Logging**: Detailed request/response logging
- **Error Handling**: Graceful error handling and user-friendly responses

## Installation

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**:
   ```bash
   cp env.example .env
   # Edit .env with your News API token
   ```

3. **Set News API Token**:
   - Get your API token from [The News API](https://thenewsapi.com/)
   - Add it to the `.env` file

## Usage

### Running the FastAPI Server

```bash
# Activate virtual environment
source venv/bin/activate.fish

# Run the server
python main.py
```

The server will start on `http://localhost:8000`

### Available Endpoints

#### News Endpoints
1. **GET /api/v1/news/top**
   - Get top news stories
   - Parameters: locale, language, categories, limit
   - Returns: JSON with stories data

2. **POST /api/v1/news/top**
   - Get top news stories (with request body)
   - Body: NewsRequest with locale, language, categories, limit
   - Returns: JSON with stories data

#### Audiobook Endpoints
3. **POST /api/v1/audiobooks/search**
   - Search for audiobooks
   - Body: AudiobookRequest with query, search_type, limit
   - Returns: JSON with audiobook search results

4. **POST /api/v1/audiobooks/play**
   - Play an audiobook by ID or search and play
   - Body: AudiobookRequest with book_id, query, play_audio
   - Returns: JSON with audiobook info and playback status

5. **GET /api/v1/audiobooks/search**
   - Search for audiobooks (GET version)
   - Parameters: query, search_type, limit
   - Returns: JSON with audiobook search results

#### Utility Endpoints
6. **GET /health**
   - Health check endpoint
   - Returns: Server status

7. **GET /**
   - Root endpoint
   - Returns: API information

### Example API Calls

#### News API Examples
```bash
# Get top news stories
curl -X GET "http://localhost:8000/api/v1/news/top?locale=us&language=en&limit=3"

# Get Spanish news
curl -X GET "http://localhost:8000/api/v1/news/top?locale=es&language=es&categories=general,sports&limit=2"

# Get international news
curl -X POST "http://localhost:8000/api/v1/news/top" \
  -H "Content-Type: application/json" \
  -d '{"locale": "international", "language": "en", "categories": ["general"], "limit": 3}'
```

#### Audiobook API Examples
```bash
# Search for audiobooks
curl -X POST "http://localhost:8000/api/v1/audiobooks/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "Alice", "search_type": "title", "limit": 3}'

# Play an audiobook
curl -X POST "http://localhost:8000/api/v1/audiobooks/play" \
  -H "Content-Type: application/json" \
  -d '{"query": "Alice in Wonderland", "search_type": "title", "play_audio": true}'

# Search by author
curl -X GET "http://localhost:8000/api/v1/audiobooks/search?query=Dickens&search_type=author&limit=2"
```

### Example Response

```json
{
  "success": true,
  "stories": [
    {
      "title": "News Title",
      "description": "News description...",
      "source": "news-source.com",
      "published_at": "2025-09-11T00:16:49.000000Z",
      "url": "https://example.com/news",
      "image_url": "https://example.com/image.jpg",
      "language": "en"
    }
  ],
  "total_count": 1,
  "language": "en",
  "locale": "us",
  "categories": ["general"]
}
```

## Configuration

### Environment Variables

- `NEWS_API_TOKEN`: Your News API token (required)
- `NEWS_API_BASE_URL`: News API base URL (default: https://api.thenewsapi.com/v1/news)
- `MCP_SERVER_NAME`: MCP server name (default: social-companion-news)
- `MCP_SERVER_VERSION`: MCP server version (default: 1.0.0)

### News Categories

Supported categories:
- `general`: General news
- `positive`: Positive/uplifting news
- `sports`: Sports news
- `culture`: Cultural news
- `entertainment`: Entertainment news
- `science`: Science news
- `health`: Health news
- `business`: Business news
- `tech`: Technology news

### Locales

Supported locales:
- `es`: Spain
- `us`: United States
- `international`: International news

## ElevenLabs Integration

To use this FastAPI server with ElevenLabs:

1. **Configure as Webhook/Tool in ElevenLabs**:
   - Add this server as a webhook or tool endpoint
   - Use the base URL: `http://your-server:8000/api/v1/news/top`
   - Configure parameters: locale, language, categories, limit

2. **Use in Agent Prompts**:
   - The agent can call the API endpoints
   - API returns structured JSON data for the agent to process
   - Filter for positive content suitable for seniors

## Error Handling

The server includes comprehensive error handling:
- API timeouts and connection errors
- Invalid parameters
- Missing API tokens
- Empty responses

All errors are returned as structured responses that the AI agent can handle gracefully.

## Development

### Project Structure

```
.
├── main.py              # Main FastAPI server
├── news_service.py      # News API service
├── config.py           # Configuration settings
├── requirements.txt    # Python dependencies
├── env.example        # Environment template
├── .env               # Environment variables (not in git)
└── README.md         # This file
```

### Testing

You can test the server by running it and making HTTP requests to the endpoints:

```bash
# Start the server
python main.py

# Test in another terminal
curl -X GET "http://localhost:8000/health"
curl -X GET "http://localhost:8000/api/v1/news/top?limit=2"
```

## License

This project is part of the Social Companionship Agent system.

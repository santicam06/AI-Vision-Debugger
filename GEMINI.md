# AI-Vision-Debugger

An automated debugging tool that identifies and solves software errors directly from screenshots of terminals, IDEs, or development environments using Vision LLMs and real-time web search.

## Project Overview
The **AI-Vision-Debugger** leverages the "Kimi K" model (via OpenRouter) to analyze visual error reports. It is specifically designed to handle version-specific breaking changes by integrating the Tavily API for live technical documentation retrieval.

### Key Technologies
- **Python**: Core logic and image processing.
- **OpenAI/OpenRouter API**: Vision model integration (Moonshot Kimi K 2.5).
- **Tavily API**: Real-time web search for up-to-date documentation.
- **PIL (Pillow)**: Image optimization and preprocessing.
- **Pydantic**: Structured tool definition for LLM function calling.

## Getting Started

### Prerequisites
- Python 3.10+
- API Keys for OpenRouter and Tavily (configured in `.env`).

### Installation
```bash
# TODO: Create requirements.txt
pip install pillow openai python-dotenv tavily-python pydantic
```

### Running the Debugger
Execute the script from the project root by providing the filename of an image located in `image_tests/`:
```bash
python src/vis-fix.py --error_1.jpeg
```

## Project Structure
- `src/vis-fix.py`: Main entry point and orchestration logic.
- `src/INSTRUCTIONS.md`: System prompt and behavioral rules for the AI analyst.
- `image_tests/`: Directory containing sample screenshots for validation.
- `sandbox_errors.txt`: Staging area for capturing error messages to be screenshotted.

## Development Conventions
- **Image Preprocessing**: Images are converted to RGB and resized to a maximum of 1024x1024 before processing to optimize latency and token costs.
- **Recursive Search**: The agent is instructed to perform sequential analysis and use `web_search` specifically when version-specific library issues are suspected.
- **Citations**: All solutions derived from external documentation must include source URLs.

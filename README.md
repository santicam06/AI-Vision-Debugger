# AI-Vision-Debugger

AI-powered debugging tool that diagnoses software errors from screenshots of terminals, IDEs, or development environments using a Vision LLM and real-time web search.

This application prints a structured diagnosis to stdout each time it is run.

## LLMs and APIs used in this application:
- [Kimi K 2.5 (moonshotai/kimi-k2.5)](https://openrouter.ai/moonshotai/kimi-k2.5)
- [Tavily Search API](https://tavily.com/): Performs web search to retrieve up-to-date documentation for debugging.


## ⚙️ Setup Instructions

Before running the application, follow these steps:

1. For this repository, create a **GitHub Codespace (Cloud)** OR clone it locally and open it with your preferred code editor (e.g. Visual Studio Code, ...).

>[!IMPORTANT]
From this point on, make sure that your present working directory on your terminal is the root directory of the application: `.\AI-Vision-Debugger`.

2. **Install Python 3.10+** (If not already installed):
   - **Windows**: Download the latest installer from [python.org](https://www.python.org/downloads/windows/) or use: `winget install Python.Python.3.12`
   - **macOS**: `brew install python`
   - **Linux (Ubuntu/Debian)**: `sudo apt update && sudo apt install python3 python3-venv python3-pip`
   - **Cloud Workspaces (Codespaces, etc.)**: Python is usually pre-installed. Run `python3 --version` to verify and skip this step.

3. **Create and Activate a Virtual Environment**:
   - Create the environment:
     - **Windows**: `python -m venv .venv`
     - **macOS/Linux**: `python3 -m venv .venv`
   - Activate it:
     - **Windows**: `.\.venv\Scripts\activate`
     - **macOS/Linux**: `source .venv/bin/activate`

4. **Install Dependencies**:
   - Upgrade `pip` and install required libraries:
     ```sh
     python -m pip install --upgrade pip
     python -m pip install -r requirements.txt
     ```

5. **Environment Configuration**:
   - Create a local `.env` file by copying the template file `.env.example`. This file contains all required API keys for the application, read and set it carefully.
   ```sh
     # Windows
     copy .env.example .env
     # macOS/Linux or PowerShell
     cp .env.example .env
   ```
> [!IMPORTANT]
> Always **copy** the template. Do not rename `.env.example` directly, as it must remain in the repository as a reference for required environment variables.

   - Open the newly created `.env` file and fill in `OPENROUTER_API_KEY` and `TAVILY_API_KEY`. The application **will not** function without a valid `.env` file in the **repository root**.

6. Directory Glossary
   - `src/`: Contains the source code.
     - `vis-fix.py`: **MAIN SCRIPT** — sends the screenshot to the vision model and orchestrates tool-calling.
     - `INSTRUCTIONS.md`: System prompt and behavioral rules for the AI analyst. 
   - `image_tests/`: Local storage for sample screenshots. The script **only reads from this directory**. Prepopulated with 3 sample bug images.
   - `sandbox_errors.txt`: Manual scratchpad for drafting error messages to later screenshot and analyze.


### 🚨 Troubleshooting
- **Missing API Key**: Ensure both `OPENROUTER_API_KEY` and `TAVILY_API_KEY` are correctly set in your `.env` file at the repository root.
- **Dependency Issues**: If running in a new environment, ensure you have executed the commands in **Step 3** onwards.
- **Virtual Environment Not Activated**: If you receive "module not found" errors, ensure your virtual environment is activated **(Step 3)**.
- **Persistent Environment Errors**: If you encounter any other unusual errors with your Python environment, manually delete the `.venv` folder and repeat the process starting from **Step 3**.
- **`ValueError: Missing image flag. Usage: --[namefile]. Include extension.`**: The CLI argument must start with `--` (double dash) and include the image extension, e.g. `--error_1.jpeg`. The image must be inside `image_tests/`.


---

## 🚀 Usage

1) Take a screenshot of the error you are having in your development environment (terminal, IDE, editor, etc.). 
    - Screenshot on Windows: `Windows key + Shift + S` (image copied to clipboard)
    - Screenshot on Mac: `Command + Shift + 4`
    - Screenshot on Linux: `Shift + Print Screen`

2) Save/Paste the picture into `./image_tests/`

Supported image formats: JPEG (.jpg, .jpeg), PNG (.png), WebP (.webp), BMP (.bmp), GIF (.gif), TIFF (.tif, .tiff)

### Run command

```bash
python src/vis-fix.py --<filename>.jpeg
```
> [!IMPORTANT]
> Pass only the basename of the image (no `image_tests/` prefix) and include the file extension. The image must be placed inside `image_tests/` beforehand.

> [!NOTE]
> Diagnostic logs (iteration traces, tool calls, errors) are written to `src/debug.txt` (overridden per run); only the final diagnosis is printed to stdout.

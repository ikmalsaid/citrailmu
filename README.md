# citrailmu

Convert lectures/talks from video/audio/YouTube into text (#GodamSahur 2025).

![CitraIlmu Web UI](assets/thumb.webp)

## Installation

```bash
pip install citrailmu
```

## Key Features

- 🎥 **Media Processing**
  - YouTube Video Support
  - Local Video/Audio Files
  - Web URL Support
  - Automatic Audio Compression
- 🔄 **Content Analysis**
  - Full Speech Transcription
  - Topic & Theme Analysis
  - Multi-language Support
  - PDF Report Generation
- 🌐 **Flexible Integration**
  - Interactive Web UI
  - Python Library
  - File & URL Processing

## Usage

### Python Library

```python
from citrailmu import CitraIlmu

# Initialize
client = CitraIlmu(
    mode="default",               # Mode (default/webui)
    api_key="YOUR_KEY",           # AI service API key
    model="gemini-1.5-flash-8b",  # AI model to use
    yt_api=False,                 # Use YouTube API (optional)
    yt_api_key="YOUR_YT_API_KEY"  # YouTube API key (optional)
)

# Process media (file/URL)
audio_file, pdf_file, markdown_text = client.process_media(
    input_path="path/to/video.mp4",     # Audio/video file path or URL
    target_language="Bahasa Malaysia",  # Target language
    processing_mode="Analysis"          # Analysis/Transcript
)
```

### Web UI

Start the Gradio web interface:

```python
client = CitraIlmu(mode="webui")
# OR
client.start_webui(
    host="0.0.0.0",      # Server host
    port=7860,           # Server port
    browser=False,       # Launch browser
    upload_size="100MB", # Max upload size
    public=False,        # Enable public URL
    limit=10,            # Max concurrent requests
    quiet=False          # Quiet mode
)
```

## Configuration

### Target Languages
- Bahasa Malaysia
- Arabic
- English
- Mandarin
- Tamil

### Processing Modes
- **Analysis**: Full content analysis with topics and themes
- **Transcript**: Complete speech-to-text conversion

### YouTube Processing Options
- **API Mode**: Uses web API for video downloading (requires API key)
- **Default Mode**: Uses native method for video downloading (no API key required)

### PDF Result Format
- Title and Overview
- Topics and Themes (Analysis mode)
- Full Transcript
- Clean Typography and Layout
- RTL Support for Arabic

## License

See [LICENSE](LICENSE) for details.

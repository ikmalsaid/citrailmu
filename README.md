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
    mode="default",              # Mode (default/webui)
    api_key="YOUR_KEY",          # AI service API key
    model="gemini-1.5-flash-8b"  # AI model to use
)

# Process media (file/URL)
audio_file, pdf_file = client.process_media(
    input_path="path/to/video.mp4",     # File path or URL
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
    port=24873,          # Server port
    browser=True,        # Launch browser
    upload_size="100MB", # Max upload size
    public=False,        # Enable public URL
    limit=10             # Max concurrent requests
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

### PDF Result Format
- Title and Overview
- Topics and Themes (Analysis mode)
- Full Transcript
- Clean Typography and Layout
- RTL Support for Arabic

## License

See [LICENSE](LICENSE) for details.

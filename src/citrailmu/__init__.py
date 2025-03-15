import os
import re
import time
import uuid
import requests
import tempfile
from datetime import datetime
from pytubefix import YouTube
from colorpaws import ColorPaws
from pytubefix.cli import on_progress
from google import generativeai as genai
from moviepy.editor import AudioFileClip
from markdown_pdf import MarkdownPdf, Section

class CitraIlmu:
    """Copyright (C) 2025 Ikmal Said. All rights reserved"""
    
    def __init__(self, mode='default', api_key=None, model='gemini-1.5-flash-8b'):
        """
        Initialize Citrailmu module.
        
        Parameters:
            mode (str): Startup mode ('default', 'webui', or 'api')
            api_key (str): API key for AI services
            model (str): AI model to use
        """
        self.logger = ColorPaws(name=self.__class__.__name__, log_on=True, log_to=None)
        self.aigc_model = model
        self.api_key = api_key
        
        self.logger.info("CitraIlmu is ready!")
        
        if mode != 'default':
            if mode == 'webui':
                self.start_wui()
            else:
                raise ValueError(f"Invalid startup mode: {mode}")

    def __is_youtube_url(self, url):
        """Check if the URL is a YouTube URL"""
        youtube_regex = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/'
        return bool(re.match(youtube_regex, url))

    def __is_url(self, url):
        """Check if string is a URL"""
        url_regex = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
        return bool(re.match(url_regex, url))

    def __format_duration(self, seconds):
        """Convert seconds to HH:MM:SS format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def __compress_audio(self, filepath, task_id):
        """Compress audio to optimal size while maintaining quality"""
        self.logger.info(f"[{task_id}] Compressing audio: {filepath}")

        try:
            filename = re.sub(r'[^\w\-]', '_', os.path.splitext(os.path.basename(filepath))[0])
            temp_path = os.path.join(tempfile.gettempdir(), f"{filename}.mp3")
            
            audio = None
            try:
                audio = AudioFileClip(filepath)
                audio = audio.audio_fadeout(0.1)
                audio.write_audiofile(
                    temp_path,
                    fps=22050,
                    nbytes=2,
                    bitrate="16k",
                    ffmpeg_params=["-ac", "1"],
                    verbose=False,
                    logger=None
                )
                return temp_path
            finally:
                if audio:
                    audio.close()
                
        except Exception as e:
            self.logger.error(f"[{task_id}] Audio compression failed: {str(e)}")
            return None

    def __media_processor(self, input_path, task_id):
        """Process media input (local file, YouTube URL, or web URL)"""
        try:
            if os.path.isfile(input_path):
                return self.__compress_audio(input_path, task_id)
            
            elif self.__is_youtube_url(input_path):
                return self.__process_youtube(input_path, task_id)
            
            elif self.__is_url(input_path):
                return self.__process_web_url(input_path, task_id)
            
            else:
                self.logger.error(f"[{task_id}] Invalid input: not a file path or URL")
                return None
                
        except Exception as e:
            self.logger.error(f"[{task_id}] Media processing failed: {str(e)}")
            return None

    def __process_youtube(self, url, task_id):
        """Process YouTube URL"""
        self.logger.info(f"[{task_id}] Processing YouTube URL: {url}")
        try:
            yt = YouTube(url, on_progress_callback=on_progress)
            temp_filename = f"{task_id}_{yt.title}.m4a"
            downloaded_file = yt.streams.get_audio_only().download(
                output_path=tempfile.gettempdir(),
                filename=temp_filename
            )
            
            compressed_audio = self.__compress_audio(downloaded_file, task_id)
            
            if os.path.exists(downloaded_file):
                os.unlink(downloaded_file)
            
            return compressed_audio
       
        except Exception as e:
            self.logger.error(f"[{task_id}] YouTube processing failed: {str(e)}")
            return None

    def __process_web_url(self, url, task_id):
        """Process web URL"""
        self.logger.info(f"[{task_id}] Processing web URL: {url}")
        try:
            filename = os.path.basename(url.split('?')[0]) or f"download_{int(time.time())}"
            temp_path = os.path.join(tempfile.gettempdir(), f"{filename}.mp4")
            
            with open(temp_path, 'wb') as f:
                response = requests.get(url, stream=True)
                if response.status_code == 200:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
            
            compressed_audio = self.__compress_audio(temp_path, task_id)
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            return compressed_audio
       
        except Exception as e:
            self.logger.error(f"[{task_id}] URL processing failed: {str(e)}")
            return None

    def __clean_markdown(self, text):
        """Clean up markdown text"""
        text = re.sub(r'```[a-zA-Z]*\n', '', text)
        text = re.sub(r'```\n?', '', text)
        return text.strip()

    def __aigc_processor(self, input_path, target_language, processing_mode, task_id):
        """Process input path using AI"""
        try:
            if self.api_key:
                genai.configure(api_key=self.api_key)

            audio = AudioFileClip(input_path)
            duration = audio.duration
            formatted_duration = self.__format_duration(duration)
            audio.close()

            if processing_mode.lower() == 'analysis':
                prompt = f"You are an expert audio transcriber and content analyst. Your task is to provide a transcript of the given audio file from 00:00 to {formatted_duration}. You must list down every discussed topic, themes, points and reflections in {target_language}. You must begin with the most suitable title of the speech with overview of the speech and must end with the conclusion. Do not include any opening or closing remarks."
            
            elif processing_mode.lower() == 'transcript':
                prompt = f"You are an expert audio transcriber. Your task is to provide a transcript of the given audio file from 00:00 to {formatted_duration}. You must begin with the most suitable title of the speech with overview of the speech. Do not include any opening or closing remarks."

            else:
                self.logger.error(f"[{task_id}] Invalid processing mode: {processing_mode}")
                return None

            audio_file = genai.upload_file(path=input_path)
            self.logger.info(f"[{task_id}] Uploading audio: {audio_file}")

            self.logger.info(f"[{task_id}] Processing AI {processing_mode}...")
            model = genai.GenerativeModel(self.aigc_model)
            response = model.generate_content([prompt, audio_file])
            
            return self.__clean_markdown(response.text)

        except Exception as e:
            self.logger.error(f"[{task_id}] AI {processing_mode} processing failed: {str(e)}")
            return None

    def __markdown_to_pdf(self, markdown_text, original_path, target_language, processing_mode, task_id):
        """Convert markdown to PDF"""
        try:
            filename = re.sub(r'[^\w\-]', '_', os.path.splitext(os.path.basename(original_path))[0])
            clean_filename = f"{filename}_{processing_mode.lower()}_{target_language.lower().replace(' ', '_')}"
            pdf_path = os.path.join(tempfile.gettempdir(), f"{clean_filename}.pdf")
            
            self.logger.info(f"[{task_id}] Generating PDF: {pdf_path}")
            pdf = MarkdownPdf(toc_level=3)
            
            # Add main content section with custom CSS
            css = """            
            body {
                font-family: 'Segoe UI', sans-serif;
                text-align: justify;
                text-justify: inter-word;
            }
            
            /* Arabic text specific */
            [lang='ar'] {
                direction: rtl;
            }
            
            table, th, td {
                border: 1px solid black;
            }
            
            h1 {
                text-align: center;
                color: #2c3e50;
                margin-top: 1.5em;
                margin-bottom: 0.8em;
                font-size: 1.25em;
                font-weight: 500;
            }
            
            h2, h3, h4, h5, h6 {
                color: #34495e;
                margin-top: 1.5em;
                margin-bottom: 0.8em;
                text-align: left;
            }
            
            p {
                margin: 0.8em 0;
            }
            """
            
            # Ensure the content starts with a level 1 header
            if not markdown_text.startswith('# '):
                if processing_mode.lower() == 'analysis':
                    title = f"CitraIlmu Analysis ({target_language})"
                
                elif processing_mode.lower() == 'transcript':
                    title = f"CitraIlmu Transcript ({target_language})"
                
                markdown_text = f"# {title}\n\n{markdown_text}"
            
            # Add the main content section
            main_section = Section(markdown_text, toc=True)
            pdf.add_section(main_section, user_css=css)
            
            # Set PDF metadata with Unicode support
            pdf.meta["title"] = title
            pdf.meta["subject"] = title
            pdf.meta["author"] = "Ikmal Said"
            pdf.meta["creator"] = "CitraIlmu"
            
            # Save the PDF
            pdf.save(pdf_path)
            return pdf_path

        except Exception as e:
            self.logger.error(f"[{task_id}] PDF generation failed: {str(e)}")
            return None

    def __get_taskid(self):
        """
        Generate a unique task ID for request tracking.
        Returns a combination of timestamp and UUID to ensure uniqueness.
        Format: YYYYMMDD_HHMMSS_UUID8
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        uuid_part = str(uuid.uuid4())[:8]
        task_id = f"{timestamp}_{uuid_part}"
        return task_id

    def process_media(self, input_path, target_language, processing_mode):
        """Process media for specified target language and processing mode.
        
        Parameters:
            input_path (str): Path to the media file
            target_language (str): Target language for the analysis ('bahasa malaysia', 'arabic', 'english', 'mandarin', 'tamil')
            processing_mode (str): Processing mode ('analysis' or 'transcript')
        """
        task_id = self.__get_taskid()
        self.logger.info(f"[{task_id}] Task started: {processing_mode} in {target_language}")

        try:
            compressed_file = self.__media_processor(input_path, task_id)
            if not compressed_file:
                return None, None
            
            markdown_text = self.__aigc_processor(compressed_file, target_language, processing_mode, task_id)
            if not markdown_text:
                return compressed_file, None
            
            pdf_file = self.__markdown_to_pdf(markdown_text, compressed_file, target_language, processing_mode, task_id)
            if not pdf_file:
                return compressed_file, None
            
            self.logger.info(f"[{task_id}] Task completed successfully")
            return compressed_file, pdf_file
            
        except Exception as e:
            self.logger.error(f"[{task_id}] Task failed: {str(e)}")
            return None, None
        
    def start_wui(self, host: str = "0.0.0.0", port: int = 24873, browser: bool = True,
                  upload_size: str = "100MB", public: bool = False, limit: int = 10):
        """
        Start Citrailmu WebUI with all features.
        
        Parameters:
        - host (str): Server host (default: "0.0.0.0")
        - port (int): Server port (default: 24873) 
        - browser (bool): Launch browser automatically (default: True)
        - upload_size (str): Maximum file size for uploads (default: "100MB")
        - public (bool): Enable public URL mode (default: False)
        - limit (int): Maximum number of concurrent requests (default: 10)
        """
        from .webui import CitraIlmuWebUI
        CitraIlmuWebUI(self, host=host, port=port, browser=browser,
                       upload_size=upload_size, public=public, limit=limit)
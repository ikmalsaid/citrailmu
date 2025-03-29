import gradio as gr

def CitraIlmuWebUI(client, host: str = None, port: int = None, browser: bool = True, upload_size: str = "4MB",
                   public: bool = False, limit: int = 10, quiet: bool = False):
    """ 
    Start Citrailmu Web UI with all features.
    
    Parameters:
    - client (Client): Citrailmu instance
    - host (str): Server host
    - port (int): Server port
    - browser (bool): Launch browser automatically
    - upload_size (str): Maximum file size for uploads
    - public (bool): Enable public URL mode
    - limit (int): Maximum number of concurrent requests
    - quiet (bool): Quiet mode
    """
    try:
        def update_preview(url):
            if not url:
                return ""
                
            template = """
            <div style="border-radius: 8px; overflow: hidden; border: 1px solid; border-color: var(--block-border-color);">
                {content}
            </div>
            """
            
            if "youtube.com" in url or "youtu.be" in url:
                video_id = url.split("v=")[1].split("&")[0] if "youtube.com" in url else url.split("/")[-1].split("?")[0]
                content = f"""
                <iframe 
                    width="100%" 
                    height="315" 
                    src="https://www.youtube.com/embed/{video_id}?rel=0" 
                    frameborder="0" 
                    allowfullscreen
                    style="display: block;">
                </iframe>
                """
            else:
                content = f"""
                <video width="100%" controls style="display: block;">
                    <source src="{url}">
                    Your browser does not support the video tag.
                </video>
                """
            
            return template.format(content=content)

        gr_css = """
        footer {
            display: none !important;
        }
        """
        
        gr_theme = gr.themes.Default(
            primary_hue="green",
            secondary_hue="green",
            neutral_hue=gr.themes.colors.zinc,
            font=["Amiri", "system-ui", "sans-serif"]
        )
    
        with gr.Blocks(title="CitraIlmu", analytics_enabled=False, theme=gr_theme, css=gr_css).queue(default_concurrency_limit=limit) as demo:
            gr.Markdown("<h1><center>CitraIlmu Web UI")
            gr.Markdown("<h3><center>Made for #GodamSahur 2025 by Ikmal Said")

            with gr.Row():
                with gr.Column():
                    with gr.Column(scale=1):
                        with gr.Tabs():                            
                            with gr.Tab('YouTube/Video URL'):
                                input_url = gr.Textbox(
                                    label="Input URL",
                                    placeholder="Enter URL...",
                                    lines=1,
                                    max_lines=1,
                                    info="Enter YouTube or web URL here"
                                )
                                url_preview = gr.HTML()
                                url_btn = gr.Button("Process URL", variant="primary")

                            with gr.Tab('Video File'):
                                input_video = gr.Video(label="Input Video File")
                                video_btn = gr.Button("Process Video", variant="primary")

                            with gr.Tab('Audio File'):
                                input_audio = gr.Audio(label="Input Audio File", type='filepath')
                                audio_btn = gr.Button("Process Audio", variant="primary")

                    with gr.Column(scale=1):
                        with gr.Tabs():
                            with gr.Tab('Settings', elem_classes='test'):
                                target_language = gr.Dropdown(
                                    value="Bahasa Malaysia", 
                                    choices=["Bahasa Malaysia", "Arabic", "English", "Mandarin", "Tamil"], 
                                    label="Target Analysis Language",
                                    info="Select the target language for the analysis"
                                )
                                processing_mode = gr.Radio(
                                    choices=["Analysis", "Transcript"],
                                    value="Analysis",
                                    label="Processing Mode",
                                    info="Analysis: Full content analysis with topics and themes | Transcript: Complete text from audio"
                                )

                    gr.Markdown("<center>")
                    gr.Markdown("<center>CitraIlmu can make mistakes. Check important info.")

                with gr.Column(scale=1):
                    with gr.Tabs():
                        with gr.Tab('Results'):
                            audio_output = gr.Audio(label="Reference Audio")
                            pdf_output = gr.File(label="Download Results as PDF")
                            with gr.Accordion("Read Results as Text"):
                                results_text = gr.Markdown(value="Please process media first for reading!", height=300)

            # Setup event handlers
            input_url.change(fn=update_preview, inputs=[input_url], outputs=[url_preview])
            audio_btn.click(fn=client.process_media, inputs=[input_audio, target_language, processing_mode], outputs=[audio_output, pdf_output, results_text])
            video_btn.click(fn=client.process_media, inputs=[input_video, target_language, processing_mode], outputs=[audio_output, pdf_output, results_text])
            url_btn.click(fn=client.process_media, inputs=[input_url, target_language, processing_mode], outputs=[audio_output, pdf_output, results_text])
        
        demo.launch(
            server_name=host,
            server_port=port,
            inbrowser=browser,
            max_file_size=upload_size,
            share=public,
            quiet=quiet
        )
    
    except Exception as e:
        client.logger.error(f"{str(e)}")
        raise
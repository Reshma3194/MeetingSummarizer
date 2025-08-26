# Meeting Summarizer - AI-Powered Meeting Insights

A modern React application that transforms meeting transcripts into actionable insights using Google's Gemini AI through a FastAPI backend. Now with **file upload support** for PDF, DOCX, TXT, WAV, and MP3 files and **sharing capabilities**!

## Features

✨ **Smart Summarization**: AI-powered meeting transcript analysis
📁 **File Upload Support**: Upload PDF, DOCX, TXT, WAV, and MP3 files directly
🎤 **Voice Input Processing**: Automatic speech-to-text conversion for audio files
🔄 **Drag & Drop**: Intuitive file upload with drag-and-drop interface
📝 **Custom Instructions**: Tailor summaries for different audiences and purposes
✏️ **Editable Results**: Modify generated summaries to perfection
📋 **Quick Presets**: Pre-built instruction templates for common use cases
📱 **Responsive Design**: Beautiful UI that works on all devices
💾 **Export Options**: Copy, download, and share summaries easily
📄 **Markdown Output**: Automatically converts summaries to professional Markdown format
📤 **Share Functionality**: Export summaries as PDF or TXT files for easy sharing

## Tech Stack

- **Frontend**: React 18 with modern hooks
- **Styling**: Tailwind CSS with custom components
- **Icons**: Lucide React for beautiful, consistent icons
- **HTTP Client**: Axios for API communication
- **Backend**: FastAPI with Gemini AI integration
- **File Processing**: PyPDF2, python-docx for document parsing
- **PDF Generation**: jsPDF for creating shareable PDF documents
- **Audio Processing**: OpenAI Whisper for speech recognition, pydub for audio handling

## Prerequisites

- Node.js 16+ and npm
- Python 3.8+ with pip
- Google Gemini API key
- FFmpeg (for audio processing)

## Installation

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd MeetingSummarizer
```

### 2. Backend Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install FFmpeg (required for audio processing)
# On Ubuntu/Debian:
sudo apt update && sudo apt install ffmpeg

# On macOS:
brew install ffmpeg

# On Windows:
# Download from https://ffmpeg.org/download.html

# Create .env file with your API key
echo "GOOGLE_API_KEY=your_actual_api_key_here" > .env

# Start the FastAPI server
python main.py
```

The backend will run on `http://localhost:8000`

### 3. Frontend Setup

```bash
# Install Node.js dependencies
npm install

# Start the React development server
npm start
```

The frontend will run on `http://localhost:3000`

## Usage

### File Upload Workflow

1. **Upload Files**: Drag and drop or click to upload PDF, DOCX, TXT, WAV, or MP3 files
2. **Content Extraction**: The app automatically extracts text content from your files
3. **Audio Processing**: Audio files are converted to text using AI speech recognition
4. **Review Content**: Preview the extracted content before summarization
5. **Customize Instructions**: Modify AI instructions or use preset templates
6. **Generate Summary**: Click "Generate Summary" to get AI-powered insights
7. **Edit & Refine**: Make adjustments using the inline Markdown editor
8. **Share & Export**: Copy, download as Markdown, or share as PDF/TXT

### Manual Input Workflow

1. **Paste Transcript**: Copy and paste your meeting transcript, call recording, or notes
2. **Customize Instructions**: Modify the AI instructions or use one of the preset templates
3. **Generate Summary**: Click "Generate Summary" to process your transcript with AI
4. **Edit & Refine**: Make adjustments to the generated summary using the inline editor
5. **Share & Export**: Copy, download, or share your final summary

### Audio File Processing

**Supported Audio Formats:**
- **WAV (.wav)**: High-quality audio files
- **MP3 (.mp3)**: Compressed audio files

**Audio Processing Features:**
- **Duration Limit**: Maximum 30 minutes per audio file
- **File Size**: Up to 100MB for audio files
- **Speech Recognition**: Uses OpenAI Whisper for accurate transcription
- **Confidence Scoring**: Shows transcription confidence level
- **Automatic Processing**: Converts speech to text seamlessly

**How It Works:**
1. Upload your audio file (WAV or MP3)
2. The system processes the audio using Whisper AI
3. Extracted transcript appears in the text area
4. Generate summary from the transcribed text
5. Edit and share as needed

### Sharing Your Summary

After generating a summary, you can share it in multiple formats:

1. **Share Button**: Click the "Share" button to open sharing options
2. **PDF Export**: Generate a professional PDF with proper formatting
3. **TXT Export**: Create a plain text file for easy sharing
4. **Copy to Clipboard**: Copy the formatted summary to paste anywhere
5. **Download Markdown**: Download the original Markdown format

## Supported File Types

- **PDF (.pdf)**: Meeting notes, reports, presentations
- **DOCX (.docx)**: Word documents, meeting minutes
- **TXT (.txt)**: Plain text files, notes
- **WAV (.wav)**: High-quality audio recordings
- **MP3 (.mp3)**: Compressed audio recordings
- **Maximum file size**: 10MB for documents, 100MB for audio files
- **Audio duration**: Maximum 30 minutes

## Export Formats

- **Markdown (.md)**: Original AI-generated format with Markdown syntax
- **PDF (.pdf)**: Professional document with proper formatting and metadata
- **TXT (.txt)**: Plain text format for universal compatibility
- **Clipboard**: Copy formatted text for pasting into other applications

## API Endpoints

- `POST /upload-file` - Upload and extract text from files (including audio)
- `POST /process-audio` - Dedicated audio processing endpoint
- `POST /summarize` - Generate AI summary from transcript and instructions
- `GET /` - Health check endpoint

## Customization

### Adding New Preset Instructions

Edit the `presetInstructions` array in `src/App.js`:

```javascript
const presetInstructions = [
  'Summarize this transcript in bullet points for a busy executive.',
  'Highlight only action items and next steps.',
  // Add your custom instructions here
  'Create a technical summary for developers.',
];
```

### Styling

The app uses Tailwind CSS with custom component classes. Modify `src/index.css` to customize:

- Color schemes
- Button styles
- Card layouts
- Animations
- Markdown content styling

## Environment Variables

Create a `.env` file in the root directory:

```env
GOOGLE_API_KEY=your_google_gemini_api_key_here
```

## Development

### Available Scripts

- `npm start` - Start development server
- `npm build` - Build for production
- `npm test` - Run tests
- `npm run eject` - Eject from Create React App

### Project Structure

```
MeetingSummarizer/
├── src/
│   ├── App.js          # Main application component with file upload and sharing
│   ├── index.js        # React entry point
│   └── index.css       # Global styles, Tailwind, and Markdown styling
├── public/
│   └── index.html      # HTML template
├── main.py             # FastAPI backend with file and audio processing
├── requirements.txt    # Python dependencies (includes Whisper)
├── package.json        # Node.js dependencies (includes jsPDF)
├── tailwind.config.js  # Tailwind configuration
└── README.md           # This file
```

## Troubleshooting

### Common Issues

1. **Import Error**: Ensure your FastAPI backend file is not named `fastapi.py`
2. **API Connection**: Verify the backend is running on port 8000
3. **CORS Issues**: CORS middleware is configured for localhost:3000
4. **Missing Dependencies**: Run `pip install -r requirements.txt` for Python deps
5. **File Upload Errors**: Check file type and size limits
6. **PDF Processing**: Ensure PyPDF2 is properly installed
7. **PDF Generation**: Make sure jsPDF is installed (`npm install jspdf`)
8. **Audio Processing**: Ensure FFmpeg is installed and accessible
9. **Whisper Model**: First audio upload will download the Whisper model (may take time)

### Getting Help

- Check the browser console for JavaScript errors
- Verify the FastAPI server is running and accessible
- Ensure your Google API key is valid and has Gemini access
- Check file upload logs in the FastAPI console
- Verify all npm dependencies are installed
- Check FFmpeg installation for audio processing

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions, please open an issue in the repository or contact the development team.

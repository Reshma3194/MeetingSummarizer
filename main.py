# main.py

import os
import uvicorn
import google.generativeai as genai
from fastapi import FastAPI, HTTPException, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import PyPDF2
import io
import docx
import tempfile
import whisper
import librosa
import numpy as np
from pydub import AudioSegment
import speech_recognition as sr

# --- 1. Load Environment Variables ---
load_dotenv()

# --- 2. Configure Gemini API Key ---
try:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("Error: GOOGLE_API_KEY not found in .env file or environment.")
    genai.configure(api_key=api_key)
except ValueError as e:
    print(e)

# --- 3. Initialize FastAPI App ---
app = FastAPI(
    title="Gemini Summarization API 🚀",
    description="A simple API to generate structured summaries from text using Google's Gemini Pro model.",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Whisper model for speech recognition
whisper_model = None

def get_whisper_model():
    global whisper_model
    if whisper_model is None:
        print("Loading Whisper model...")
        whisper_model = whisper.load_model("base")
        print("Whisper model loaded successfully!")
    return whisper_model

# --- 4. Define Pydantic Models for Data Validation ---
class SummarizeRequest(BaseModel):
    transcript: str = Field(
        ...,
        min_length=20,
        description="The full text transcript that needs to be summarized."
    )
    instruction: str = Field(
        default="Summarize this transcript in bullet points for a busy executive.",
        min_length=10,
        description="The specific instruction for the AI (e.g., 'List all action items')."
    )

class SummarizeResponse(BaseModel):
    summary: str = Field(
        description="The generated summary based on the provided transcript and instruction."
    )

class FileUploadResponse(BaseModel):
    content: str = Field(description="Extracted text content from the uploaded file")
    filename: str = Field(description="Name of the uploaded file")
    file_type: str = Field(description="Type of the uploaded file")

class AudioUploadResponse(BaseModel):
    transcript: str = Field(description="Transcribed text from the audio file")
    filename: str = Field(description="Name of the uploaded audio file")
    file_type: str = Field(description="Type of the uploaded file")
    duration: float = Field(description="Duration of the audio in seconds")
    confidence: float = Field(description="Confidence score of the transcription")

# --- 5. File Processing Functions ---
def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF file content"""
    try:
        pdf_file = io.BytesIO(file_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error processing PDF file: {str(e)}"
        )

def extract_text_from_docx(file_content: bytes) -> str:
    """Extract text from DOCX file content"""
    try:
        doc_file = io.BytesIO(file_content)
        doc = docx.Document(doc_file)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text.strip()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error processing DOCX file: {str(e)}"
        )

def extract_text_from_txt(file_content: bytes) -> str:
    """Extract text from TXT file content"""
    try:
        return file_content.decode('utf-8').strip()
    except UnicodeDecodeError:
        try:
            return file_content.decode('latin-1').strip()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error processing TXT file: {str(e)}"
            )

def process_audio_file(file_content: bytes, filename: str) -> dict:
    """Process audio file and extract transcript using Whisper"""
    try:
        # Save audio file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name
        
        try:
            # Load audio file
            audio = AudioSegment.from_file(temp_file_path)
            
            # Check duration (max 30 minutes = 1800 seconds)
            duration_seconds = len(audio) / 1000.0
            if duration_seconds > 1800:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Audio file is too long. Maximum allowed duration is 30 minutes."
                )
            
            # Convert to WAV format for Whisper
            wav_path = temp_file_path.replace(os.path.splitext(filename)[1], '.wav')
            audio.export(wav_path, format="wav")
            
            # Load Whisper model and transcribe
            model = get_whisper_model()
            result = model.transcribe(wav_path)
            
            # Clean up temporary files
            os.unlink(temp_file_path)
            os.unlink(wav_path)
            
            return {
                "transcript": result["text"].strip(),
                "duration": duration_seconds,
                "confidence": result.get("confidence", 0.0)
            }
            
        except Exception as e:
            # Clean up temporary file on error
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            raise e
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error processing audio file: {str(e)}"
        )

# --- 6. File Upload Endpoint ---
@app.post("/upload-file",
          response_model=FileUploadResponse,
          tags=["File Upload"],
          summary="Upload and extract text from files")
async def upload_file(
    file: UploadFile = File(..., description="File to upload (PDF, DOCX, TXT, WAV, or MP3)"),
    instruction: str = Form(default="Summarize this document in bullet points for a busy executive.")
):
    """
    Upload a file (PDF, DOCX, TXT, WAV, or MP3) and extract its text content.
    The extracted text can then be used for summarization.
    """
    # Validate file type
    allowed_types = {
        "application/pdf": "pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
        "text/plain": "txt",
        "audio/wav": "wav",
        "audio/mpeg": "mp3",
        "audio/mp3": "mp3",
        "audio/x-wav": "wav"
    }
    
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type. Please upload PDF, DOCX, TXT, WAV, or MP3 files only."
        )
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Extract text based on file type
        file_type = allowed_types[file.content_type]
        
        if file_type in ["wav", "mp3"]:
            # Process audio file
            audio_result = process_audio_file(file_content, file.filename)
            extracted_text = audio_result["transcript"]
        elif file_type == "pdf":
            extracted_text = extract_text_from_pdf(file_content)
        elif file_type == "docx":
            extracted_text = extract_text_from_docx(file_content)
        elif file_type == "txt":
            extracted_text = extract_text_from_txt(file_content)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported file type"
            )
        
        if not extracted_text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No text content could be extracted from the file"
            )
        
        return FileUploadResponse(
            content=extracted_text,
            filename=file.filename,
            file_type=file_type
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file: {str(e)}"
        )

# --- 7. Audio Processing Endpoint ---
@app.post("/process-audio",
          response_model=AudioUploadResponse,
          tags=["Audio Processing"],
          summary="Process audio file and extract transcript")
async def process_audio(
    file: UploadFile = File(..., description="Audio file to process (WAV or MP3, max 30 minutes)")
):
    """
    Process an audio file and extract the transcript using speech recognition.
    Supports WAV and MP3 files up to 30 minutes in length.
    """
    # Validate audio file type
    allowed_audio_types = {
        "audio/wav": "wav",
        "audio/mpeg": "mp3",
        "audio/mp3": "mp3",
        "audio/x-wav": "wav"
    }
    
    if file.content_type not in allowed_audio_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please upload only WAV or MP3 audio files."
        )
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Get file type
        file_type = allowed_audio_types[file.content_type]

        # Process audio file
        result = process_audio_file(file_content, file.filename)
        
        return AudioUploadResponse(
            transcript=result["transcript"],
            filename=file.filename,
            file_type=file_type,
            duration=result["duration"],
            confidence=result["confidence"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing audio file: {str(e)}"
        )

# --- 8. Enhanced Summarization Endpoint ---
@app.post("/summarize",
          response_model=SummarizeResponse,
          tags=["Summarization"],
          summary="Generate a text summary")
async def summarize_text(request: SummarizeRequest):
    """
    Accepts a text transcript and a custom instruction, then returns a
    summary generated by the Gemini Pro model.
    """
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        full_prompt = f"""
        Your task is to process the text transcript provided below based on a specific instruction.

        Instruction:
        "{request.instruction}"

        Transcript:
        ---
        {request.transcript}
        ---

        Now, generate the response that fulfills the instruction.
        """
        
        response = model.generate_content(full_prompt)
        return SummarizeResponse(summary=response.text)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing the request: {str(e)}"
        )

# --- 9. Add a Root Endpoint for Health Checks ---
@app.get("/", tags=["Health Check"])
def read_root():
    """A simple health check endpoint to confirm the API is running."""
    return {"status": "OK", "message": "Welcome to the Gemini Summarization API!"}

# This block allows running the app directly with `python main.py`
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
    
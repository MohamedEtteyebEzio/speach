import streamlit as st
import speech_recognition as sr
from pydub import AudioSegment
import tempfile
import os
import datetime

# Define supported APIs
SUPPORTED_APIS = {
    'Google Web Speech API': 'google',
    'Sphinx': 'sphinx',
    'Wit.ai': 'wit',
    'Microsoft Bing Voice Recognition': 'bing',
    'Houndify': 'houndify'
}

# Define supported languages
SUPPORTED_LANGUAGES = {
    'English': 'en-US',
    'Spanish': 'es-ES',
    'French': 'fr-FR',
    'German': 'de-DE',
    'Italian': 'it-IT',
    'Portuguese': 'pt-PT',
    'Dutch': 'nl-NL',
    'Russian': 'ru-RU',
    'Chinese (Simplified)': 'zh-CN',
    'Japanese': 'ja-JP'
}

def transcribe_speech(api='google', language='en-US'):
    # Initialize recognizer class
    r = sr.Recognizer()
    # Reading Microphone as source
    with sr.Microphone() as source:
        st.info("Speak now...")
        # listen for speech and store in audio_text variable
        try:
            audio_text = r.listen(source)
            st.info("Transcribing...")
        except sr.WaitTimeoutError:
            return "No speech detected. Please try speaking again."
        except sr.UnknownValueError:
            return "Could not understand audio. Please try speaking more clearly."
        except sr.RequestError as e:
            return f"Could not request results from microphone; {str(e)}"
        except Exception as e:
            return f"An unexpected error occurred while recording: {str(e)}"

        try:
            # Use the selected API
            if api == 'google':
                text = r.recognize_google(audio_text, language=language)
            elif api == 'sphinx':
                text = r.recognize_sphinx(audio_text)
            elif api == 'wit':
                # Note: Requires WIT_AI_KEY environment variable
                try:
                    text = r.recognize_wit(
                        audio_text, 
                        key=os.getenv('WIT_AI_KEY'),
                        language=language
                    )
                except sr.UnknownValueError:
                    return "Could not understand audio using Wit.ai"
                except sr.RequestError:
                    return "Could not request results from Wit.ai service. Please check your API key."
            elif api == 'bing':
                # Note: Requires BING_KEY environment variable
                try:
                    text = r.recognize_bing(
                        audio_text, 
                        key=os.getenv('BING_KEY'),
                        language=language
                    )
                except sr.UnknownValueError:
                    return "Could not understand audio using Microsoft Bing"
                except sr.RequestError:
                    return "Could not request results from Microsoft Bing service. Please check your API key."
            elif api == 'houndify':
                # Note: Requires HOUNDIFY_CLIENT_ID and HOUNDIFY_CLIENT_KEY
                try:
                    text = r.recognize_houndify(
                        audio_text,
                        client_id=os.getenv('HOUNDIFY_CLIENT_ID'),
                        client_key=os.getenv('HOUNDIFY_CLIENT_KEY'),
                        language=language
                    )
                except sr.UnknownValueError:
                    return "Could not understand audio using Houndify"
                except sr.RequestError:
                    return "Could not request results from Houndify service. Please check your API credentials."
            return text
        except sr.UnknownValueError:
            return "Sorry, I did not understand what you said. Please try speaking more clearly."
        except sr.RequestError as e:
            return f"Could not request results from {api} service; {str(e)}"
        except Exception as e:
            return f"An unexpected error occurred during transcription: {str(e)}"

def transcribe_mp3(file, api='google', language='en-US'):
    try:
        # Check if ffmpeg is installed
        try:
            import subprocess
            subprocess.run(['ffmpeg', '-version'], capture_output=True)
        except:
            return "Error: FFmpeg is not installed. Please install FFmpeg from: https://ffmpeg.org/download.html"

        # Convert MP3 to WAV
        audio = AudioSegment.from_mp3(file)
        
        # Create temporary WAV file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
            temp_wav_path = temp_wav.name
            audio.export(temp_wav_path, format='wav')
            
        # Initialize recognizer
        r = sr.Recognizer()
        
        # Read the WAV file
        with sr.AudioFile(temp_wav_path) as source:
            audio_data = r.record(source)
            try:
                # Use the selected API
                if api == 'google':
                    text = r.recognize_google(audio_data, language=language)
                elif api == 'sphinx':
                    text = r.recognize_sphinx(audio_data)
                elif api == 'wit':
                    # Note: Requires WIT_AI_KEY environment variable
                    text = r.recognize_wit(
                        audio_data, 
                        key=os.getenv('WIT_AI_KEY'),
                        language=language
                    )
                elif api == 'bing':
                    # Note: Requires BING_KEY environment variable
                    text = r.recognize_bing(
                        audio_data, 
                        key=os.getenv('BING_KEY'),
                        language=language
                    )
                elif api == 'houndify':
                    # Note: Requires HOUNDIFY_CLIENT_ID and HOUNDIFY_CLIENT_KEY
                    text = r.recognize_houndify(
                        audio_data,
                        client_id=os.getenv('HOUNDIFY_CLIENT_ID'),
                        client_key=os.getenv('HOUNDIFY_CLIENT_KEY'),
                        language=language
                    )
                return text
            except sr.UnknownValueError:
                return "Sorry, I did not understand what you said."
            except sr.RequestError as e:
                return f"Could not request results from {api} service; {str(e)}"
            
        # Clean up temporary file
        try:
            os.unlink(temp_wav_path)
        except:
            pass  # If we can't delete the file, it's not critical
            
    except Exception as e:
        # Try to clean up the temporary file if it exists
        try:
            if 'temp_wav_path' in locals():
                os.unlink(temp_wav_path)
        except:
            pass
        return f"Error processing MP3 file: {str(e)}\nPlease make sure FFmpeg is properly installed and added to your system PATH."

def save_transcription(text, filename=None):
    """
    Save the transcribed text to a file.
    If no filename is provided, use a timestamp-based filename.
    """
    if not filename:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"transcription_{timestamp}.txt"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(text)
        return f"Transcription saved successfully to: {filename}"
    except Exception as e:
        return f"Error saving transcription: {str(e)}"

def main():
    st.title("Speech Recognition App")
    st.write("Choose your input method:")
    
    # Add API selection dropdown
    selected_api = st.selectbox(
        "Select Speech Recognition API",
        list(SUPPORTED_APIS.keys()),
        help="Note: Some APIs may require API keys to be set in your environment variables"
    )
    
    # Add language selection dropdown
    selected_language = st.selectbox(
        "Select Language",
        list(SUPPORTED_LANGUAGES.keys()),
        help="Select the language you are speaking in"
    )
    
    # Add tabs for different input methods
    tab1, tab2 = st.tabs(["Record Audio", "Upload MP3"])
    
    with tab1:
        st.write("Click on the microphone to start speaking:")
        if st.button("Start Recording"):
            text = transcribe_speech(
                SUPPORTED_APIS[selected_api],
                SUPPORTED_LANGUAGES[selected_language]
            )
            st.write("Transcription: ", text)
            
            # Add save button
            if st.button("Save Transcription"): 
                result = save_transcription(text)
                st.write(result)
    
    with tab2:
        st.write("Upload an MP3 file to transcribe:")
        uploaded_file = st.file_uploader("Choose an MP3 file", type=["mp3"])
        if uploaded_file is not None:
            if st.button("Transcribe MP3"):
                text = transcribe_mp3(
                    uploaded_file,
                    SUPPORTED_APIS[selected_api],
                    SUPPORTED_LANGUAGES[selected_language]
                )
                st.write("Transcription: ", text)
                
                # Add save button
                if st.button("Save Transcription"): 
                    result = save_transcription(text)
                    st.write(result)

if __name__ == "__main__":
    main()

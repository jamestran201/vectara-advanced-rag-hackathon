# vectara-advanced-rag-hackathon

## Generating transcripts

The lecture videos are from [this course](https://pdos.csail.mit.edu/6.824/schedule.html). The videos are downloaded through `youtube-dl` and converted into audio files using `ffmpeg`. The audio files are then placed in the `audio_files` directory.

Running the script `upload_audio_files.py` (with an AssemblyAI API key) will upload all audio files in the `audio_files` directory so that they can be used for transcribing later. This script will write the uploaded file URLs to the `uploaded_files.txt` file.

Run the script `transcribe.py` to create the transcripts for each lecture. The generated transcripts are located at `transcripts/`.
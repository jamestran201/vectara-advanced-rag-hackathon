import os
import requests

API_KEY = os.getenv("ASSEMBLY_AI_API_KEY", "")
if API_KEY == "":
    raise ValueError("Must set a value for ASSEMBLY_AI_API_KEY environment variable")

def upload_audio_file(file_path):
    url = "https://api.assemblyai.com/v2/upload"
    headers = {
        'Authorization': API_KEY,
        'Content-Type': 'application/octet-stream',
    }

    with open(file_path, 'rb') as f:
        data = f.read()

    response = requests.post(url, headers=headers, data=data)
    response_json = response.json()
    print(f"Status: {response.status_code}, Upload URL: {response_json['upload_url']}, File: {file_path}")
    return response_json['upload_url']

directory = 'audio_files'
with open("uploaded_files.txt", "w") as f:
    for filename in os.listdir(directory):
        if filename.endswith(".mp3"):
            file_path = os.path.join(directory, filename)
            upload_url = upload_audio_file(file_path)
            line = f"{filename}: {upload_url}\n"
            f.write(line)
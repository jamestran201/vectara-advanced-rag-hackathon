import assemblyai as aai
import json
import os

API_KEY = os.getenv("ASSEMBLY_AI_API_KEY", "")
if API_KEY == "":
    raise ValueError("Must set a value for ASSEMBLY_AI_API_KEY environment variable")

aai.settings.api_key = API_KEY

file_url_by_lectures = {}

with open("uploaded_files.txt", "r") as f:
    for line in f.readlines():
        filename, file_url = line.strip().split(": ")
        lecture_name = filename.removesuffix(".mp3")
        file_url_by_lectures[lecture_name] = file_url

for lecture_name, file_url in file_url_by_lectures.items():
    print(f"Transcribing {lecture_name}")

    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(file_url)

    if transcript.status == aai.TranscriptStatus.error:
        print(f"Failed to transcribe {lecture_name}: {transcript.error}")
        continue

    print(f"Successfully transcribed {lecture_name}, fetching paragraphs")

    vectara_doc = {
        "documentId": lecture_name,
        "section": []
    }
    paragraphs = transcript.get_paragraphs()
    for pa in paragraphs:
        metadata = { "start": pa.start // 1000, "end": pa.end // 1000 } # Divide by 1000 to convert from ms to s
        section = {
            "text": pa.text,
            "metadataJson": json.dumps(metadata, separators=(',', ':'))
        }
        vectara_doc["section"].append(section)

    with open(f"{lecture_name}_transcript.json", "w") as f:
        json.dump(vectara_doc, f)

    print(f"Created {lecture_name}_transcript.json")
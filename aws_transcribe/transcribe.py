import os
import time

import boto3
import pandas as pd

from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())  # read local .env file

transcribe = boto3.client(
    "transcribe",
    aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
    region_name="eu-west-1",
)


# def check_job_name(job_name):
#     job_verification = True  # all the transcriptions
#     existed_jobs = transcribe.list_transcription_jobs()
#     for job in existed_jobs["TranscriptionJobSummaries"]:
#         if job_name == job["TranscriptionJobName"]:
#             job_verification = False
#             break
#         if job_verification == False:
#             command = input(
#                 job_name
#                 + " has existed. \nDo you want to override the existed job (Y/N): "
#             )
#             if command.lower() == "y" or command.lower() == "yes":
#                 transcribe.delete_transcription_job(TranscriptionJobName=job_name)
#         elif command.lower() == "n" or command.lower() == "no":
#             job_name = input("Insert new job name? ")
#             check_job_name(job_name)
#         else:
#             print("Input can only be (Y/N)")
#             command = input(
#                 job_name
#                 + " has existed. \nDo you want to override the existed job (Y/N): "
#             )
#     return job_name


def amazon_transcribe(audio_file_name, max_speakers=-1):
    if max_speakers > 10:
        raise ValueError("Maximum detected speakers is 10.")

    job_uri = "s3://transcribe-rpg/" + audio_file_name
    job_name = (audio_file_name.split(".")[0] + str(time.time_ns())).replace(" ", "")
    job_language = "fr-FR"

    # check if name is taken or not
    # job_name = check_job_name(job_name)

    if max_speakers != -1:
        transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={"MediaFileUri": job_uri},
            MediaFormat=audio_file_name.split(".")[1],
            LanguageCode=job_language,
            Settings={"ShowSpeakerLabels": True, "MaxSpeakerLabels": max_speakers},
        )
    else:
        transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={"MediaFileUri": job_uri},
            MediaFormat=audio_file_name.split(".")[1],
            LanguageCode=job_language,
            Settings={"ShowSpeakerLabels": True},
        )

    json_data = pd.DataFrame({}, index=['transcripts', 'speaker_labels', 'items'])
    while True:
        result = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        if result["TranscriptionJob"]["TranscriptionJobStatus"] in [
            "COMPLETED",
            "FAILED",
        ]:
            break
        time.sleep(15)
    if result["TranscriptionJob"]["TranscriptionJobStatus"] == "COMPLETED":
        json_data = pd.read_json(
            result["TranscriptionJob"]["Transcript"]["TranscriptFileUri"]
        )

    return result, json_data

def compress_items(json_items):

    current_speaker = None
    current_sentence = []
    total_diarization = []

    for s in json_items:
        speaker = s['speaker_label']
        text = s['alternatives'][0]['content']

        if speaker != current_speaker:
            if len(current_sentence) > 0:
                total_diarization.append({current_speaker:" ".join(current_sentence)})

            current_sentence = [text]
            current_speaker = speaker
        else:
            current_sentence.append(text)

    if len(current_sentence) > 0:
        total_diarization.append({current_speaker:" ".join(current_sentence)})

    return total_diarization

if __name__ == "__main__":
    result, json_data = amazon_transcribe("session4_20231216204613.wav", 3)

    # print("RESULT:", result, sep="\n", end="\n\n")
    # print("TRANSCRIPTS:", json_data.loc['transcripts']['results'], sep="\n", end="\n\n")
    # print("SPEAKER_LABELS:", json_data.loc['speaker_labels']['results'], sep="\n", end="\n\n")
    # print("ITEMS:", json_data.loc['items']['results'], sep="\n", end="\n\n")

    json_items = json_data.loc['items']['results']
    diarization = compress_items(json_items)
    output = "\n".join([ f"{k}: {v}" for d in diarization for k,v in d.items()])

    print(output)
    with open("output.txt", "a") as f:
        f.writelines(f"{output}\n")
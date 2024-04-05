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

def check_job_name(job_name):
    job_verification = True  # all the transcriptions
    existed_jobs = transcribe.list_transcription_jobs()
    for job in existed_jobs["TranscriptionJobSummaries"]:
        if job_name == job["TranscriptionJobName"]:
            job_verification = False
            break
        if job_verification == False:
            command = input(
                job_name
                + " has existed. \nDo you want to override the existed job (Y/N): "
            )
            if command.lower() == "y" or command.lower() == "yes":
                transcribe.delete_transcription_job(TranscriptionJobName=job_name)
        elif command.lower() == "n" or command.lower() == "no":
            job_name = input("Insert new job name? ")
            check_job_name(job_name)
        else:
            print("Input can only be (Y/N)")
            command = input(
                job_name
                + " has existed. \nDo you want to override the existed job (Y/N): "
            )
    return job_name


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

    data = None
    while True:
        result = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        if result["TranscriptionJob"]["TranscriptionJobStatus"] in [
            "COMPLETED",
            "FAILED",
        ]:
            break
        time.sleep(15)
    if result["TranscriptionJob"]["TranscriptionJobStatus"] == "COMPLETED":
        data = pd.read_json(
            result["TranscriptionJob"]["Transcript"]["TranscriptFileUri"]
        )

    return result, data


result, data = amazon_transcribe("session4_20231216204613.wav", 3)
print(result)
print(data)

# https://s3.eu-west-1.amazonaws.com/aws-transcribe-eu-west-1-prod/807818147787/session4_202312162046131712331763509694903/d50e6f33-4d6f-47df-8d5f-d4e51001efc2/asrOutput.json?X-Amz-Security-Token=IQoJb3JpZ2luX2VjEH8aCWV1LXdlc3QtMSJHMEUCIQCG6lL5bHk71qjVRcldnq9wU0TBcZHFC%2Bfid6VSPsrQgAIgZy5dhFJMP3sfpfVnt0s%2FYlV5vYWkVyRLgkDEjHr7uZ0quwUIp%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARAEGgw1ODcwMTc2NjM0MTciDERcjzJLrDrsr9Hx2iqPBUKs3hwr7N%2B6wYGNFnXBcCQUDAc5aoIkBauotMcSyj%2BaIOg4JPG7Uzutec3B8lhnYB9Gt86ArrH1BQzflLcZouk7UuPeGK4f3KUlKNAgLbwSSN6jJoWgTTLDRGXRLZt1osuTL4KXorvaBDOFsJlFM4NvRZfFL1xi6f91T3jn7giYumFuUiGt%2BG4yt8AH2GZ5p%2FdkxNH2I9r9VfGDEHTwR0iaPx56%2Bg9TUU0HZFSBGxI92Dm7zSX9%2FudWzo%2F53mmgzzFUH1GL3hSzm1sd3sDIo84swnyS7yk%2FDqpGx%2Fd9TfFx46HkMZqkBZKduQMvSYFE2n5RExUCtI3OQTfQxVj72kCFzvULAX0LwsFESTgYtY2NP9JEygZaWW19%2BRXSL3BKIFZ5EX4xhTFqaLS4K5iskVcgGw6otdMzbNjUctDxQnjE3QY51ziNoK2Fw7vXfBARCvEl5wsc4TNqcTAovJ9LAmjWwFYpzRieK4gGanFMPoGprnE5bPpdvc2usIH7LBUkknfYkt8rp6UvKXH0poSRC7qP0qwGTX%2ByzYyB5TP4zxrdyuXmHs5gYM5gJgaIy%2B5%2BEbq909yRvA4b59SEA0rF5V20LdgG2Kos3HmjGmVsFjVwIkXC2bu2Yxu7dNMLNtvyJ6hmY2BHg6NjE5%2BdyT%2Fgly4MIH6CJetMWu8L%2BGGb7libqINcFOe4oIxuj8XTkcdE4KdB%2Fk6isukkEQjRUP1X0ToK%2FfesSKUfZSSZl0UC1GFp5498rCy%2B9HOTq7eW8QT3KakuMiNzIL78YCuaMNLEhYzDAvnW2jvJ571fBWioz97tDQZKCLvYF2AecxbhHaY62faqUPuA8VKOxYiI9j7wqRwAFB6K0%2B%2Fu1%2BSpSlZ6Ah8w95DAsAY6sQEy60P%2FeZytFFOlSwDxccDGtce0M25V%2F8te%2BighHofucBrz7hNykBZyeabC2WL%2Bq%2FCmG5E5UDXhZ7ZeDVSSXU%2BTfB%2FV3E%2Bw2ckQFZA075zeSWnmp%2FCzcBiY6%2Bb9nLmpxR%2FesyFDdxMvXDVkfzk0bHUcAcbRonQt7WpFNv06hsoE78ZmAKcvnxRSZ%2BQPLTPpBF7T2E8RoJBd0dvo5Pot8KAFKwRe16%2FHzV5CcTuaCwIx%2BUU%3D&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20240405T154344Z&X-Amz-SignedHeaders=host&X-Amz-Expires=900&X-Amz-Credential=ASIAYRLH2WO43MYYYAL6%2F20240405%2Feu-west-1%2Fs3%2Faws4_request&X-Amz-Signature=6a350acd14452ae4a1c50afc0ca94ced83ef94d852669ae4f41234c4ea2bea74
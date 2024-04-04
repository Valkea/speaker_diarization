import os
import time
import azure.cognitiveservices.speech as speechsdk

from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())  # read local .env file


def conversation_transcriber_recognition_canceled_cb(evt: speechsdk.SessionEventArgs):
    print("Canceled event")


def conversation_transcriber_session_stopped_cb(evt: speechsdk.SessionEventArgs):
    print("SessionStopped event")


def conversation_transcriber_transcribed_cb(evt: speechsdk.SpeechRecognitionEventArgs):
    print("TRANSCRIBED:")
    if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
        output = f"{evt.result.speaker_id}: {evt.result.text}"
        print(output)
        with open("output.txt", "a") as f:
            f.write(f"{output}\n")
    elif evt.result.reason == speechsdk.ResultReason.NoMatch:
        print(
            "\tNOMATCH: Speech could not be TRANSCRIBED: {}".format(
                evt.result.no_match_details
            )
        )


def conversation_transcriber_session_started_cb(evt: speechsdk.SessionEventArgs):
    print("SessionStarted event")


def recognize_from_file(file_name, language="en-US"):
    speech_config = speechsdk.SpeechConfig(
        subscription=os.environ.get("SPEECH_KEY"),
        region=os.environ.get("SPEECH_REGION"),
        speech_recognition_language=language,
    )

    audio_config = speechsdk.audio.AudioConfig(filename=file_name)
    conversation_transcriber = speechsdk.transcription.ConversationTranscriber(
        speech_config=speech_config, audio_config=audio_config
    )

    transcribing_stop = False

    def stop_cb(evt: speechsdk.SessionEventArgs):
        # """callback that signals to stop continuous recognition upon receiving an event `evt`"""
        print("CLOSING on {}".format(evt))
        nonlocal transcribing_stop
        transcribing_stop = True

    # Connect callbacks to the events fired by the conversation transcriber
    conversation_transcriber.transcribed.connect(
        conversation_transcriber_transcribed_cb
    )
    conversation_transcriber.session_started.connect(
        conversation_transcriber_session_started_cb
    )
    conversation_transcriber.session_stopped.connect(
        conversation_transcriber_session_stopped_cb
    )
    conversation_transcriber.canceled.connect(
        conversation_transcriber_recognition_canceled_cb
    )
    # stop transcribing on either session stopped or canceled events
    conversation_transcriber.session_stopped.connect(stop_cb)
    conversation_transcriber.canceled.connect(stop_cb)

    conversation_transcriber.start_transcribing_async()

    # Waits for completion.
    while not transcribing_stop:
        time.sleep(0.5)

    conversation_transcriber.stop_transcribing_async()


# Main

try:
    # Languages: https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support?tabs=stt
    # recognize_from_file("katiesteve.wav", "en-US")
    # recognize_from_file("session4_20231216204613.wav", "fr-FR")
    recognize_from_file("session4_20231216204807.wav", "fr-FR")
except Exception as err:
    print("Encountered exception. {}".format(err))

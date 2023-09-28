import os
import time


def say(
        text: str,
        language: str = 'en-US',
        lib: str = "gtts",
        cache_file: str = "./.cache/tts.mp3",
        delay: float = 0.1,
):
    """
    Say the text using the default system voice.

    :param text: The text to say.
    :type text: str
    :param language: The language to use to say the text.
    :type language: str
    :param lib: The library to use to generate the audio file.
    :type lib: str
    :param cache_file: The path to the cache file.
    :type cache_file: str
    :param delay: delay in seconds to play the audio.
    :type delay: float

    :return: The result of the request.
    """
    known_libs = {
        "gtts": gen_audio_with_gtts,
        "pyttsx3": gen_audio_with_pyttsx3,
    }
    try:
        import playsound
    except ImportError:
        raise ImportError("The package playsound must be installed.")

    if lib not in known_libs:
        raise ValueError(f"Unknown lib: {lib}")

    cache_file = known_libs[lib](text, language, cache_file)
    time.sleep(delay)
    playsound.playsound(os.path.abspath(cache_file))
    return cache_file


def gen_audio_with_gtts(
        text: str,
        language: str = 'en-US',
        cache_file: str = "./.cache/gtts/tts.mp3",
):
    """
    Generate the audio file using gtts.

    :param text: The text to say.
    :type text: str
    :param language: The language to use to say the text.
    :type language: str
    :param cache_file: The path to the cache file.

    :return: The result of the request.
    """
    import gtts
    os.makedirs(os.path.dirname(cache_file), exist_ok=True)
    gtts.gTTS(text, lang=language).save(cache_file)
    return cache_file


def gen_audio_with_pyttsx3(
        text: str,
        language: str = 'en-US',
        cache_file: str = "./.cache/pyttsx3/tts.mp3",
):
    """
    Generate the audio file using pyttsx3.

    :param text: The text to say.
    :type text: str
    :param language: The language to use to say the text.
    :type language: str
    :param cache_file: The path to the cache file.

    :return: The result of the request.
    """
    import pyttsx3
    os.makedirs(os.path.dirname(cache_file), exist_ok=True)
    engine = pyttsx3.init()
    engine.save_to_file(text, cache_file)
    engine.runAndWait()
    return cache_file


if __name__ == '__main__':
    say("Your code has finished.", language="en", lib="gtts")

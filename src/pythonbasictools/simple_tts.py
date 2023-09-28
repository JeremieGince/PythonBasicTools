import os
import time
from .decorators import try_func_n_times


def say(
        text: str,
        language: str = 'en-US',
        lib: str = "gtts",
        cache_file: str = "./.cache/tts.mp3",
        rm_cache_file: bool = True,
        raise_error: bool = False,
        n_trials: int = 32,
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
    :param rm_cache_file: Whether to remove the cache file after playing it.
    :type rm_cache_file: bool

    :return: The result of the request.
    """
    known_libs = {
        "gtts": gen_audio_with_gtts,
        "pyttsx3": gen_audio_with_pyttsx3,
    }
    try:
        import playsound
    except ImportError:
        raise ImportError("The package playsound must be installed. You can install it with `pip install playsound`.")

    if lib not in known_libs:
        raise ValueError(f"Unknown lib: {lib}. Known libs: {known_libs.keys()}.")

    def trial(_text, _language, _cache_file):
        _cache_file = known_libs[lib](_text, _language, _cache_file)
        time.sleep(delay)
        playsound.playsound(os.path.abspath(_cache_file))
        return _cache_file
    try:
        try_func_n_times(trial, n=n_trials, delay=delay)(text, language, cache_file)
    except Exception as e:
        if raise_error:
            raise e
        else:
            print(e)
    finally:
        if rm_cache_file:
            if os.path.exists(cache_file):
                os.remove(cache_file)
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
    try:
        import gtts
    except ImportError:
        raise ImportError("The package gtts must be installed. You can install it with `pip install gtts`.")
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
    try:
        import pyttsx3
    except ImportError:
        raise ImportError("The package pyttsx3 must be installed. You can install it with `pip install pyttsx3`.")
    os.makedirs(os.path.dirname(cache_file), exist_ok=True)
    engine = pyttsx3.init()
    engine.setVoice(language)
    engine.save_to_file(text, cache_file)
    engine.runAndWait()
    return cache_file


if __name__ == '__main__':
    say("Your code has finished.", language="en", lib="gtts")

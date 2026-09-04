import keyring


SERVICE_NAME = "NexaMind"
GEMINI_KEY_NAME = "GEMINI_API_KEY"


def save_gemini_key(api_key: str):
    keyring.set_password(
        SERVICE_NAME,
        GEMINI_KEY_NAME,
        api_key
    )


def get_gemini_key():
    return keyring.get_password(
        SERVICE_NAME,
        GEMINI_KEY_NAME
    )


def delete_gemini_key():
    try:
        keyring.delete_password(
            SERVICE_NAME,
            GEMINI_KEY_NAME
        )
    except keyring.errors.PasswordDeleteError:
        pass


def is_gemini_key_configured():
    return bool(get_gemini_key())
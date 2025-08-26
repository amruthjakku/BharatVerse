# backend/core/settings.py

import os

from dotenv import load_dotenv

# Load environment variables from the .env file in the `backend` directory
load_dotenv()


class Settings:
    """
    Holds all the application settings, loaded from environment variables.
    This provides a single, reliable source for all configurations.
    """

    # Base URL for the external Telugu Corpus Collections API
    CORPUS_API_BASE_URL: str = os.getenv(
        "CORPUS_API_BASE_URL", "https://api.corpus.swecha.org"
    )

    # We might need an API token later for authenticated requests
    CORPUS_API_TOKEN: str = os.getenv("CORPUS_API_TOKEN")


# Create a single instance of the Settings class that we can import elsewhere
settings = Settings()

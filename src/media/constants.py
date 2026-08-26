from pathlib import Path

MAX_FILE_SIZE = 5 * 1024 * 1024
MAX_FILE_SIZE_FOR_MESSAGE = 5
ALLOWED_FILE_TYPES = ['JPEG', 'PNG']
BASE_DIR = Path(__file__).resolve().parents[2]
IMAGES_DIR = BASE_DIR / 'images'

ALLOWED_CONTENT_TYPES = {
    'image/jpeg',
    'image/png',
}

import hashlib

from markitdown import MarkItDown
from sanic.request import File


def bytes_to_string(size_in_bytes: int) -> str:
    if size_in_bytes == 0:
        return "0 B"

    units = ("B", "KB", "MB", "GB", "TB")
    i = min(4, int(size_in_bytes.bit_length() / 10))
    size = size_in_bytes / (1 << (i * 10))

    return f"{size:.1f} {units[i]}" if size >= 100 else f"{size:.2f} {units[i]}"


def convert_to_markdown(file: File) -> str:
    md = MarkItDown()
    result = md.convert_stream(file.body, file_extension=file.name.split(".")[-1])
    return result.text_content


def generate_content_hash(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()

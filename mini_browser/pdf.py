"""
PDF text extraction for mini-browser.
Tries pdfplumber first (better accuracy), falls back to pypdf.
"""


def extract_pdf(data: bytes) -> str | None:
    """Extract text from PDF bytes. Returns None if extraction fails."""
    text = _try_pdfplumber(data)
    if text:
        return text
    return _try_pypdf(data)


def _try_pdfplumber(data: bytes) -> str | None:
    try:
        import io
        import pdfplumber

        pages: list[str] = []
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            for page in pdf.pages[:25]:
                t = page.extract_text()
                if t:
                    pages.append(t.strip())
        text = "\n\n".join(pages)
        return text if len(text.split()) > 20 else None
    except Exception:
        return None


def _try_pypdf(data: bytes) -> str | None:
    try:
        import io
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(data))
        pages: list[str] = []
        for page in reader.pages[:25]:
            t = page.extract_text()
            if t:
                pages.append(t.strip())
        text = "\n\n".join(pages)
        return text if len(text.split()) > 20 else None
    except Exception:
        return None


def is_pdf_url(url: str) -> bool:
    return url.lower().split("?")[0].endswith(".pdf")


def is_pdf_response(content_type: str) -> bool:
    return "application/pdf" in content_type.lower()

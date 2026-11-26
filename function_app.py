import logging

import azure.functions as func

from sanitizer import EvidenceInvalid, EvidenceTooLarge, sanitize_image

app = func.FunctionApp()


@app.blob_trigger(arg_name="raw", path="evidences-raw/{name}", connection="EVIDENCE_STORAGE")
@app.blob_output(arg_name="clean", path="evidences-sanitized/{name}.jpg", connection="EVIDENCE_STORAGE")
def media_sanitizer(raw: func.InputStream, clean: func.Out[bytes]) -> None:
    data = raw.read()
    try:
        clean.set(sanitize_image(data))
        logging.info("evidence_sanitized name=%s in_bytes=%d", raw.name, len(data))
    except EvidenceTooLarge:
        logging.warning("evidence_rejected_too_large name=%s bytes=%d", raw.name, len(data))
    except EvidenceInvalid:
        logging.warning("evidence_rejected_invalid name=%s", raw.name)

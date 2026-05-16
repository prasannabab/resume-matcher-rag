SECTION_HEADERS = [
    "skills",
    "experience",
    "projects",
    "education",
    "summary",
    "certifications"
]


def chunk_resume(text):

    chunks = []

    current_section = "general"

    current_content = []

    lines = text.splitlines()

    for line in lines:

        clean_line = line.strip()

        if not clean_line:
            continue

        lower = clean_line.lower()

        matched_section = None

        for section in SECTION_HEADERS:

            if section in lower:
                matched_section = section
                break

        if matched_section:

            if current_content:

                chunks.append({
                    "chunk_type": current_section,
                    "chunk_text": "\n".join(current_content)
                })

            current_section = matched_section

            current_content = []

        else:
            current_content.append(clean_line)

    if current_content:

        chunks.append({
            "chunk_type": current_section,
            "chunk_text": "\n".join(current_content)
        })

    return chunks

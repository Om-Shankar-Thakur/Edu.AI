# text_chunking.py

def chunk_course_row(row):
    """
    Convert a dataframe row into a clean text block used for vector embedding.
    """

    fields = [
        ("Title", row.get("title", "")),
        ("Short Intro", row.get("short_intro", "")),
        ("Category", row.get("category", "")),
        ("Sub Category", row.get("sub-category", "")),
        ("Type", row.get("course_type", "")),
        ("Language", row.get("language", "")),
        ("Skills", row.get("skills", "")),
        ("Instructors", row.get("instructors", "")),
        ("Rating", str(row.get("rating", ""))),
        ("URL", row.get("url", "")),
    ]

    text = "\n".join(f"{k}: {v}" for k, v in fields if v)
    return text

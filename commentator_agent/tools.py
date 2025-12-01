"""
Tools for the commentator agent.
"""

import pathlib


def save_cup_summary_to_mark_down(filename: str, content: str) -> dict[str, str]:
    """
    Saves the given content to a Markdown file in the current directory.
    """
    try:
        if not filename.endswith(".md"):
            filename += ".md"
        current_directory = pathlib.Path.cwd()
        file_path = current_directory / filename
        file_path.write_text(content, encoding="utf-8")
        return {
            "status": "success",
            "message": f"Successfully saved news to {file_path.resolve()}",
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to save file: {str(e)}"}

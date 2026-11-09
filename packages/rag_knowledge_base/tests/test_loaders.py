
from pathlib import Path

import pytest

from packages.rag_knowledge_base.ingestion.loaders import MarkdownLoader


def test_load_file_extracts_content_and_metadata(tmp_path: Path) -> None:
    knowledge_root = tmp_path / "knowledge"
    projects = knowledge_root / "projects"
    projects.mkdir(parents=True)

    file_path = projects / "incidentpilot.md"
    file_path.write_text(
        "# IncidentPilot\n\nAn agentic incident analysis project.",
        encoding="utf-8",
    )

    document = MarkdownLoader().load_file(file_path, knowledge_root)

    assert document.id == "projects/incidentpilot.md"
    assert document.metadata.source == "projects/incidentpilot.md"
    assert document.metadata.category == "projects"
    assert document.metadata.title == "Incidentpilot"
    assert "agentic incident analysis" in document.content


def test_load_directory_finds_nested_markdown_files(tmp_path: Path) -> None:
    root = tmp_path / "knowledge"
    (root / "projects").mkdir(parents=True)
    (root / "profile.md").write_text("Portfolio profile", encoding="utf-8")
    (root / "projects" / "incidentpilot.md").write_text(
        "IncidentPilot project", encoding="utf-8"
    )
    (root / "notes.txt").write_text("Ignore this", encoding="utf-8")

    documents = MarkdownLoader().load_directory(root)

    assert len(documents) == 2
    assert [document.id for document in documents] == [
        "profile.md",
        "projects/incidentpilot.md",
    ]


def test_loader_rejects_paths_outside_knowledge_root(tmp_path: Path) -> None:
    root = tmp_path / "knowledge"
    root.mkdir()
    external_file = tmp_path / "secret.md"
    external_file.write_text("Not knowledge", encoding="utf-8")

    with pytest.raises(ValueError, match="inside the knowledge directory"):
        MarkdownLoader().load_file(external_file, root)


def test_loader_rejects_empty_markdown(tmp_path: Path) -> None:
    root = tmp_path / "knowledge"
    root.mkdir()
    empty_file = root / "empty.md"
    empty_file.write_text("   \n", encoding="utf-8")

    with pytest.raises(ValueError, match="empty"):
        MarkdownLoader().load_file(empty_file, root)


def test_loader_rejects_unsupported_file_type(tmp_path: Path) -> None:
    root = tmp_path / "knowledge"
    root.mkdir()
    file_path = root / "notes.txt"
    file_path.write_text("Plain text", encoding="utf-8")

    with pytest.raises(ValueError, match="Unsupported file type"):
        MarkdownLoader().load_file(file_path, root)

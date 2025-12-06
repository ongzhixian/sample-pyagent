import os

class FileService:
    """Service class for safe file and directory management."""

    def __init__(self, root: str = "./data"):
        # All operations are restricted under this root directory
        self.root = os.path.abspath(root)
        os.makedirs(self.root, exist_ok=True)

    def _resolve_path(self, path: str) -> str:
        """Resolve and validate path to ensure it's inside the root."""
        abs_path = os.path.abspath(os.path.join(self.root, path))
        if not abs_path.startswith(self.root):
            raise PermissionError(f"Access denied: '{path}' is outside allowed root.")
        return abs_path

    # -----------------------------
    # File Operations
    # -----------------------------
    def read_file(self, path: str) -> str:
        abs_path = self._resolve_path(path)
        if not os.path.exists(abs_path):
            return f"Error: File '{path}' does not exist."
        try:
            with open(abs_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            return f"Error reading file '{path}': {e}"

    def write_file(self, path: str, content: str) -> str:
        abs_path = self._resolve_path(path)
        try:
            with open(abs_path, "w", encoding="utf-8") as f:
                f.write(content)
            return f"Successfully wrote to '{path}'."
        except Exception as e:
            return f"Error writing to file '{path}': {e}"

    def append_file(self, path: str, content: str) -> str:
        abs_path = self._resolve_path(path)
        try:
            with open(abs_path, "a", encoding="utf-8") as f:
                f.write(content)
            return f"Successfully appended to '{path}'."
        except Exception as e:
            return f"Error appending to file '{path}': {e}"

    def delete_file(self, path: str) -> str:
        abs_path = self._resolve_path(path)
        if not os.path.isfile(abs_path):
            return f"Error: '{path}' is not a valid file."
        try:
            os.remove(abs_path)
            return f"File '{path}' deleted successfully."
        except Exception as e:
            return f"Error deleting file '{path}': {e}"

    # -----------------------------
    # Directory Operations
    # -----------------------------
    def list_files(self, directory: str = "") -> list[str]:
        abs_path = self._resolve_path(directory)
        if not os.path.isdir(abs_path):
            return [f"Error: '{directory}' is not a valid directory."]
        try:
            return os.listdir(abs_path)
        except Exception as e:
            return [f"Error listing files in '{directory}': {e}"]

    def create_directory(self, directory: str) -> str:
        abs_path = self._resolve_path(directory)
        try:
            os.makedirs(abs_path, exist_ok=True)
            return f"Directory '{directory}' created successfully."
        except Exception as e:
            return f"Error creating directory '{directory}': {e}"

    def remove_directory(self, directory: str) -> str:
        abs_path = self._resolve_path(directory)
        if not os.path.isdir(abs_path):
            return f"Error: '{directory}' is not a valid directory."
        try:
            os.rmdir(abs_path)
            return f"Directory '{directory}' removed successfully."
        except Exception as e:
            return f"Error removing directory '{directory}': {e}"

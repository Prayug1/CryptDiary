import os
import json
from datetime import datetime
from pathlib import Path


class DiaryStorage:
    """Manages storage of encrypted diary entries"""

    def __init__(self, storage_path="diary_entries", user_dir=None):
        """
        Initialize DiaryStorage

        Args:
            storage_path: Directory path for storing diary entries (relative to user_dir if provided)
            user_dir: User-specific directory for multi-user support
        """
        if user_dir:
            self.storage_path = Path(user_dir) / storage_path
        else:
            self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        self.index_file = self.storage_path / "index.json"
        self._load_index()

    def _load_index(self):
        """Load the diary entries index"""
        if self.index_file.exists():
            with open(self.index_file, 'r') as f:
                self.index = json.load(f)
        else:
            self.index = {'entries': []}

    def _save_index(self):
        """Save the diary entries index"""
        with open(self.index_file, 'w') as f:
            json.dump(self.index, f, indent=2)

    def save_entry(self, title, encrypted_data, tags=None):
        """
        Save encrypted diary entry

        Args:
            title: Entry title
            encrypted_data: Encrypted entry data from CryptoManager
            tags: Optional list of tags

        Returns:
            Entry ID
        """
        # Generate entry ID
        entry_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

        # Create entry metadata
        entry_metadata = {
            'id': entry_id,
            'title': title,
            'created': datetime.now().isoformat(),
            'modified': datetime.now().isoformat(),
            'tags': tags or [],
            'filename': f"{entry_id}.json"
        }

        # Save encrypted entry data
        entry_file = self.storage_path / entry_metadata['filename']
        with open(entry_file, 'w') as f:
            json.dump(encrypted_data, f, indent=2)

        # Update index
        self.index['entries'].append(entry_metadata)
        self._save_index()

        return entry_id

    def update_entry(self, entry_id, title=None, encrypted_data=None, tags=None):
        """
        Update existing diary entry

        Args:
            entry_id: Entry ID to update
            title: New title (optional)
            encrypted_data: New encrypted data (optional)
            tags: New tags (optional)

        Returns:
            True if successful, False otherwise
        """
        # Find entry in index
        entry_metadata = None
        for entry in self.index['entries']:
            if entry['id'] == entry_id:
                entry_metadata = entry
                break

        if not entry_metadata:
            return False

        # Update metadata
        if title is not None:
            entry_metadata['title'] = title
        if tags is not None:
            entry_metadata['tags'] = tags
        entry_metadata['modified'] = datetime.now().isoformat()

        # Update encrypted data if provided
        if encrypted_data is not None:
            entry_file = self.storage_path / entry_metadata['filename']
            with open(entry_file, 'w') as f:
                json.dump(encrypted_data, f, indent=2)

        self._save_index()
        return True

    def load_entry(self, entry_id):
        """
        Load encrypted diary entry

        Args:
            entry_id: Entry ID to load

        Returns:
            Tuple (metadata, encrypted_data) or (None, None) if not found
        """
        # Find entry in index
        entry_metadata = None
        for entry in self.index['entries']:
            if entry['id'] == entry_id:
                entry_metadata = entry
                break

        if not entry_metadata:
            return None, None

        # Load encrypted data
        entry_file = self.storage_path / entry_metadata['filename']
        if not entry_file.exists():
            return None, None

        with open(entry_file, 'r') as f:
            encrypted_data = json.load(f)

        return entry_metadata, encrypted_data

    def delete_entry(self, entry_id):
        """
        Delete diary entry

        Args:
            entry_id: Entry ID to delete

        Returns:
            True if successful, False otherwise
        """
        # Find and remove from index
        entry_metadata = None
        for i, entry in enumerate(self.index['entries']):
            if entry['id'] == entry_id:
                entry_metadata = self.index['entries'].pop(i)
                break

        if not entry_metadata:
            return False

        # Delete entry file
        entry_file = self.storage_path / entry_metadata['filename']
        if entry_file.exists():
            entry_file.unlink()

        self._save_index()
        return True

    def list_entries(self):
        """
        List all diary entries

        Returns:
            List of entry metadata dictionaries
        """
        # Sort by creation date (newest first)
        sorted_entries = sorted(
            self.index['entries'],
            key=lambda x: x['created'],
            reverse=True
        )
        return sorted_entries

    def search_entries(self, query):
        """
        Search entries by title or tags

        Args:
            query: Search query string

        Returns:
            List of matching entry metadata
        """
        query_lower = query.lower()
        matching_entries = []

        for entry in self.index['entries']:
            # Check title
            if query_lower in entry['title'].lower():
                matching_entries.append(entry)
                continue

            # Check tags
            for tag in entry.get('tags', []):
                if query_lower in tag.lower():
                    matching_entries.append(entry)
                    break

        # Sort by creation date (newest first)
        sorted_entries = sorted(
            matching_entries,
            key=lambda x: x['created'],
            reverse=True
        )
        return sorted_entries

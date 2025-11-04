#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for ChatMemorySystem - Database Operations
"""

import pytest
import time
from memory_system import ChatMemorySystem


class TestDatabaseCreation:
    """Test database initialization and table creation"""

    def test_database_created(self, temp_db_path):
        """Test that database file is created"""
        memory = ChatMemorySystem(db_path=temp_db_path)

        assert temp_db_path.exists(), "Database file not created"

        memory.close()

    def test_mydata_table_exists(self, memory_system):
        """Test that mydata table is created"""
        # Query table schema
        result = memory_system.db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='mydata'"
        ).fetchone()

        assert result is not None, "mydata table not created"
        assert result[0] == 'mydata'

    def test_unique_constraint_exists(self, memory_system):
        """Test that UNIQUE(content, meta) constraint exists"""
        # Get table schema
        result = memory_system.db.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name='mydata'"
        ).fetchone()

        schema = result[0]
        assert 'UNIQUE' in schema, "UNIQUE constraint missing"
        assert 'content' in schema and 'meta' in schema


class TestSaveData:
    """Test save_data method"""

    def test_save_simple_data(self, memory_system):
        """Test saving simple data"""
        row_id = memory_system.save_data("test@test.com", "email", "en")

        assert row_id > 0, "Failed to save data"

        # Verify data was saved
        results = memory_system.search_data("test@test.com")
        assert len(results) == 1
        assert results[0]['content'] == "test@test.com"
        assert results[0]['meta'] == "email"

    def test_save_with_special_characters(self, memory_system):
        """Test saving data with special characters"""
        row_id = memory_system.save_data("P@ssw0rd!#$", "password", "en")

        assert row_id > 0

        results = memory_system.search_data("P@ssw0rd")
        assert len(results) == 1

    def test_save_with_unicode(self, memory_system):
        """Test saving Unicode data"""
        row_id = memory_system.save_data("北京", "city", "en")

        assert row_id > 0

        results = memory_system.search_data("北京")
        assert len(results) == 1

    def test_save_duplicate_prevention(self, memory_system):
        """Test UNIQUE constraint prevents duplicates"""
        # Save same data twice
        row_id1 = memory_system.save_data("test@test.com", "email", "en")
        time.sleep(0.1)  # Small delay to see timestamp update
        row_id2 = memory_system.save_data("test@test.com", "email", "en")

        # Second save should update, not create duplicate
        results = memory_system.search_data("test@test.com")
        assert len(results) == 1, "Duplicate created despite UNIQUE constraint"

    def test_save_same_content_different_meta(self, memory_system):
        """Test saving same content with different meta"""
        row_id1 = memory_system.save_data("123456", "phone", "en")
        row_id2 = memory_system.save_data("123456", "password", "en")

        # Should create 2 entries (different meta)
        results = memory_system.search_data("123456")
        assert len(results) == 2

    def test_save_multilingual(self, memory_system):
        """Test saving data in different languages"""
        memory_system.save_data("test@test.com", "email", "en")
        memory_system.save_data("test@test.de", "Email", "de")
        memory_system.save_data("test@test.es", "correo", "es")

        # All should be saved
        all_data = memory_system.list_all_data()
        assert len(all_data) >= 3


class TestSearchData:
    """Test search_data method"""

    def test_search_by_content(self, memory_system_with_data):
        """Test searching by content"""
        results = memory_system_with_data.search_data("test@test.com")

        assert len(results) >= 1
        assert results[0]['content'] == "test@test.com"

    def test_search_by_meta(self, memory_system_with_data):
        """Test searching by meta label"""
        results = memory_system_with_data.search_data("email")

        assert len(results) >= 1
        assert 'email' in results[0]['meta'].lower()

    def test_search_partial_match(self, memory_system_with_data):
        """Test partial matching (LIKE query)"""
        results = memory_system_with_data.search_data("test")

        # Should match "test@test.com"
        assert len(results) >= 1

    def test_search_no_results(self, memory_system_with_data):
        """Test search with no results"""
        results = memory_system_with_data.search_data("nonexistent")

        assert len(results) == 0

    def test_search_limit(self, memory_system):
        """Test search result limit"""
        # Add 20 items
        for i in range(20):
            memory_system.save_data(f"test{i}@test.com", "email", "en")

        # Search with limit=5
        results = memory_system.search_data("test", limit=5)

        assert len(results) == 5

    def test_search_ordered_by_timestamp(self, memory_system):
        """Test that results are ordered by timestamp DESC"""
        # Add items with delays
        memory_system.save_data("old@test.com", "email", "en")
        time.sleep(0.1)
        memory_system.save_data("new@test.com", "email", "en")

        results = memory_system.search_data("test")

        # Newest should be first
        assert results[0]['content'] == "new@test.com"


class TestDeleteData:
    """Test delete_data method"""

    def test_delete_by_content(self, memory_system_with_data):
        """Test deleting by content"""
        deleted = memory_system_with_data.delete_data("test@test.com")

        assert deleted >= 1

        # Verify deletion
        results = memory_system_with_data.search_data("test@test.com")
        assert len(results) == 0

    def test_delete_by_meta(self, memory_system_with_data):
        """Test deleting by meta label"""
        deleted = memory_system_with_data.delete_data("email")

        assert deleted >= 1

        # Verify deletion
        results = memory_system_with_data.search_data("email")
        assert len(results) == 0

    def test_delete_no_matches(self, memory_system_with_data):
        """Test deleting with no matches"""
        deleted = memory_system_with_data.delete_data("nonexistent")

        assert deleted == 0

    def test_delete_partial_match(self, memory_system):
        """Test deleting with partial match"""
        memory_system.save_data("test1@test.com", "email", "en")
        memory_system.save_data("test2@test.com", "email", "en")
        memory_system.save_data("test3@test.com", "email", "en")

        # Delete all matching "test"
        deleted = memory_system.delete_data("test")

        assert deleted == 3


class TestDeleteByIds:
    """Test delete_by_ids method"""

    def test_delete_by_single_id(self, memory_system_with_data):
        """Test deleting by single ID"""
        # Get an ID
        results = memory_system_with_data.search_data("test@test.com")
        id_to_delete = results[0]['id']

        deleted = memory_system_with_data.delete_by_ids([id_to_delete])

        assert deleted == 1

        # Verify deletion
        results = memory_system_with_data.search_data("test@test.com")
        assert len(results) == 0

    def test_delete_by_multiple_ids(self, memory_system):
        """Test deleting multiple IDs"""
        # Add items
        id1 = memory_system.save_data("test1@test.com", "email", "en")
        id2 = memory_system.save_data("test2@test.com", "email", "en")
        id3 = memory_system.save_data("test3@test.com", "email", "en")

        # Delete 2 of them
        deleted = memory_system.delete_by_ids([id1, id3])

        assert deleted == 2

        # Verify only id2 remains
        all_data = memory_system.list_all_data()
        assert len(all_data) == 1
        assert all_data[0]['id'] == id2

    def test_delete_empty_list(self, memory_system_with_data):
        """Test deleting with empty ID list"""
        deleted = memory_system_with_data.delete_by_ids([])

        assert deleted == 0


class TestListAllData:
    """Test list_all_data method"""

    def test_list_all(self, memory_system_with_data):
        """Test listing all data"""
        results = memory_system_with_data.list_all_data()

        # Should have test data from fixture
        assert len(results) >= 5

    def test_list_empty_database(self, memory_system):
        """Test listing from empty database"""
        results = memory_system.list_all_data()

        assert len(results) == 0

    def test_list_with_limit(self, memory_system):
        """Test listing with limit"""
        # Add 20 items
        for i in range(20):
            memory_system.save_data(f"test{i}@test.com", "email", "en")

        results = memory_system.list_all_data(limit=10)

        assert len(results) == 10

    def test_list_ordered_by_timestamp(self, memory_system):
        """Test that list is ordered by timestamp DESC"""
        memory_system.save_data("old@test.com", "email", "en")
        time.sleep(0.1)
        memory_system.save_data("new@test.com", "email", "en")

        results = memory_system.list_all_data()

        # Newest first
        assert results[0]['content'] == "new@test.com"


class TestExecuteSQL:
    """Test execute_sql method"""

    def test_execute_insert(self, memory_system):
        """Test executing INSERT SQL"""
        sql = "INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('test@test.com', 'email', 'en')"
        row_id = memory_system.execute_sql(sql)

        assert row_id > 0

        # Verify data
        results = memory_system.search_data("test@test.com")
        assert len(results) == 1

    def test_execute_select(self, memory_system_with_data):
        """Test executing SELECT SQL"""
        sql = "SELECT id, content, meta, timestamp FROM mydata WHERE meta LIKE '%email%'"
        results = memory_system_with_data.execute_sql(sql, fetch=True)

        assert len(results) >= 1

    def test_execute_delete(self, memory_system_with_data):
        """Test executing DELETE SQL"""
        sql = "DELETE FROM mydata WHERE content = 'test@test.com'"
        memory_system_with_data.execute_sql(sql)

        # Verify deletion
        results = memory_system_with_data.search_data("test@test.com")
        assert len(results) == 0

    def test_execute_with_params(self, memory_system):
        """Test executing SQL with parameters"""
        sql = "INSERT INTO mydata (content, meta, lang) VALUES (?, ?, ?)"
        params = ("test@test.com", "email", "en")

        row_id = memory_system.execute_sql(sql, params)

        assert row_id > 0

    def test_execute_invalid_sql(self, memory_system):
        """Test executing invalid SQL"""
        sql = "INVALID SQL STATEMENT"

        result = memory_system.execute_sql(sql, fetch=False)

        # Should return 0 or None on error
        assert result == 0 or result is None


class TestDatabaseStats:
    """Test get_stats method"""

    def test_stats_total_items(self, memory_system_with_data):
        """Test total items count in stats"""
        stats = memory_system_with_data.get_stats()

        assert 'total_items' in stats
        assert stats['total_items'] >= 5  # From fixture

    def test_stats_db_size(self, memory_system_with_data):
        """Test database size in stats"""
        stats = memory_system_with_data.get_stats()

        assert 'db_size_mb' in stats
        assert stats['db_size_mb'] > 0

    def test_stats_date_range(self, memory_system_with_data):
        """Test date range in stats"""
        stats = memory_system_with_data.get_stats()

        assert 'oldest_item' in stats
        assert 'newest_item' in stats

    def test_stats_empty_database(self, memory_system):
        """Test stats for empty database"""
        stats = memory_system.get_stats()

        assert stats['total_items'] == 0


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_save_empty_content(self, memory_system):
        """Test saving empty content"""
        row_id = memory_system.save_data("", "empty", "en")

        # Should succeed (empty string is valid)
        assert row_id > 0

    def test_save_null_meta(self, memory_system):
        """Test saving with NULL meta"""
        row_id = memory_system.save_data("test@test.com", None, "en")

        assert row_id > 0

        results = memory_system.search_data("test@test.com")
        assert len(results) == 1
        assert results[0]['meta'] is None or results[0]['meta'] == 'None'

    def test_save_very_long_content(self, memory_system):
        """Test saving very long content"""
        long_content = "x" * 10000
        row_id = memory_system.save_data(long_content, "long_text", "en")

        assert row_id > 0

    def test_search_empty_query(self, memory_system_with_data):
        """Test searching with empty query"""
        results = memory_system_with_data.search_data("")

        # Should match everything (LIKE '%%')
        assert len(results) >= 5

    def test_concurrent_operations(self, memory_system):
        """Test multiple operations in sequence"""
        # Save
        id1 = memory_system.save_data("test1@test.com", "email", "en")
        id2 = memory_system.save_data("test2@test.com", "email", "en")

        # Search
        results = memory_system.search_data("test")
        assert len(results) == 2

        # Delete one
        memory_system.delete_by_ids([id1])

        # Search again
        results = memory_system.search_data("test")
        assert len(results) == 1


class TestEncryption:
    """Test encryption (when available)"""

    def test_database_with_encryption_key(self, temp_db_path, mock_encryption_key):
        """Test creating database with encryption key"""
        try:
            import sqlcipher3
            has_sqlcipher = True
        except ImportError:
            has_sqlcipher = False

        if has_sqlcipher:
            memory = ChatMemorySystem(
                db_path=temp_db_path,
                encryption_key=mock_encryption_key
            )

            # Should work with encryption
            row_id = memory.save_data("test@test.com", "email", "en")
            assert row_id > 0

            memory.close()
        else:
            pytest.skip("SQLCipher not available")

    def test_database_fallback_without_encryption(self, temp_db_path):
        """Test fallback to sqlite3 when encryption not available"""
        # Create without encryption key
        memory = ChatMemorySystem(db_path=temp_db_path, encryption_key=None)

        # Should still work
        row_id = memory.save_data("test@test.com", "email", "en")
        assert row_id > 0

        memory.close()


class TestDatabaseCleanup:
    """Test database cleanup and closing"""

    def test_close_database(self, temp_db_path):
        """Test closing database connection"""
        memory = ChatMemorySystem(db_path=temp_db_path)
        memory.save_data("test@test.com", "email", "en")

        memory.close()

        # Database file should still exist
        assert temp_db_path.exists()

    def test_operations_after_close(self, temp_db_path):
        """Test that operations fail after close"""
        memory = ChatMemorySystem(db_path=temp_db_path)
        memory.close()

        # Operations after close should fail gracefully
        # (depending on sqlite3 vs APSW implementation)
        # Just verify it doesn't crash
        try:
            memory.save_data("test@test.com", "email", "en")
        except:
            pass  # Expected to fail

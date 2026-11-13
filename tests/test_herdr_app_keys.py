import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import herdr_app_keys as keys_tool  # noqa: E402


class KeysTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = Path(self.dir.name) / "keys.json"

    def tearDown(self):
        self.dir.cleanup()

    def write(self, data):
        self.path.write_text(json.dumps(data))

    def read(self):
        return json.loads(self.path.read_text())

    def test_add_binds_key_and_keeps_others(self):
        self.write({"global": {"cmd-t": "tab.new"}, "terminal": {"cmd-c": "terminal.copy"}})
        self.assertEqual(keys_tool.main(["add", str(self.path)]), 0)
        self.assertEqual(
            self.read(),
            {"global": {"cmd-t": "tab.new", "ctrl-a i": "mod.open:ids"}, "terminal": {"cmd-c": "terminal.copy"}},
        )
        self.assertTrue(self.path.with_name("keys.json.ids-backup").exists())

    def test_add_refuses_conflict_and_changes_nothing(self):
        self.write({"global": {"ctrl-a i": "tab.new"}})
        self.assertEqual(keys_tool.main(["check", str(self.path)]), 1)
        self.assertEqual(keys_tool.main(["add", str(self.path)]), 1)
        self.assertEqual(self.read(), {"global": {"ctrl-a i": "tab.new"}})
        self.assertFalse(self.path.with_name("keys.json.ids-backup").exists())

    def test_add_twice_writes_once(self):
        self.write({"global": {"ctrl-a i": "mod.open:ids"}})
        self.assertEqual(keys_tool.main(["add", str(self.path)]), 0)
        self.assertFalse(self.path.with_name("keys.json.ids-backup").exists())

    def test_remove_only_our_binding(self):
        self.write({"global": {"ctrl-a i": "mod.open:ids", "cmd-t": "tab.new"}})
        self.assertEqual(keys_tool.main(["remove", str(self.path)]), 0)
        self.assertEqual(self.read(), {"global": {"cmd-t": "tab.new"}})
        self.write({"global": {"ctrl-a i": "tab.new"}})
        self.assertEqual(keys_tool.main(["remove", str(self.path)]), 0)
        self.assertEqual(self.read(), {"global": {"ctrl-a i": "tab.new"}})

    def test_bad_files_fail_without_writing(self):
        self.assertEqual(keys_tool.main(["check", str(self.path)]), 1)
        self.assertFalse(self.path.exists())
        self.path.write_text("{not json")
        self.assertEqual(keys_tool.main(["add", str(self.path)]), 1)
        self.write({"global": []})
        self.assertEqual(keys_tool.main(["add", str(self.path)]), 1)

    def test_usage(self):
        self.assertEqual(keys_tool.main(["bind", str(self.path)]), 2)


if __name__ == "__main__":
    unittest.main()

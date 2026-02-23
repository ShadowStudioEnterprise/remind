from fakes import FakeWindow

def test_save_entry_adds_entry(monkeypatch):
    from src.remind.controllers.app_controller import AppController
    from src.remind.core.models import MigraineEntry

    w = FakeWindow()
    settings = type("S", (), {"language":"es"})()
    entries = []

    # mock save_history si aplica
    monkeypatch.setattr("remind.core.storage.save_history", lambda e: None)

    c = AppController(window=w, settings=settings, entries=entries)
    ok = c.save_entry(True, 5, "test")

    assert ok is True
    assert len(entries) == 1
    assert isinstance(entries[0], MigraineEntry)
class FakeWindow:
    def __init__(self):
        self.status = []
        self.errors = []
        self.entries = None
    def show_status(self, text, ms=0): self.status.append((text, ms))
    def show_error(self, title, msg): self.errors.append((title, msg))
    def set_entries(self, entries): self.entries = entries
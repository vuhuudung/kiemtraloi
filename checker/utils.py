def load_wordlist(path):
    with open(path, encoding="utf-8") as f:
        return set(line.strip().lower() for line in f if line.strip())

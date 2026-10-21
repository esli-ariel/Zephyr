"""Créer une copie cohérente de SQLite, même lorsque l'API fonctionne."""
import argparse
import sqlite3
from contextlib import closing
from pathlib import Path


def backup_database(source: str, destination: str) -> Path:
    source_path = Path(source).expanduser().resolve()
    target = Path(destination).expanduser().resolve()
    # mode=ro refuse une source absente au lieu de créer une base vide.
    with closing(sqlite3.connect(source_path.as_uri() + "?mode=ro", uri=True)) as reader:
        # Ne jamais remplacer une sauvegarde existante.
        with target.open("xb"):
            pass
        try:
            with closing(sqlite3.connect(target)) as writer:
                reader.backup(writer)
                if writer.execute("PRAGMA quick_check").fetchone()[0] != "ok":
                    raise RuntimeError("La copie SQLite est invalide.")
        except BaseException:
            target.unlink(missing_ok=True)
            raise
    return target


if __name__ == "__main__":
    from app.config import settings

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", help="Chemin d'un nouveau fichier .sqlite3")
    args = parser.parse_args()
    print(backup_database(settings.database_path, args.destination))

"""Local accounts, hashed passwords and revocable opaque sessions in SQLite."""
import hashlib
import hmac
import json
import secrets
import sqlite3
import time
from contextlib import closing
from pathlib import Path
from uuid import uuid4

SCRYPT_N = 2 ** 17
SCRYPT_R = 8
SCRYPT_P = 1
SESSION_SECONDS = 7 * 24 * 3600
COOKIE_NAME = 'zephyr_session'


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode('utf-8'), salt=salt, n=SCRYPT_N,
                            r=SCRYPT_R, p=SCRYPT_P, dklen=32, maxmem=256 * 1024 * 1024)
    return f'scrypt${SCRYPT_N}${SCRYPT_R}${SCRYPT_P}${salt.hex()}${digest.hex()}'


def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, n, r, p, salt, expected = encoded.split('$')
        if algorithm != 'scrypt' or (int(n), int(r), int(p)) != (SCRYPT_N, SCRYPT_R, SCRYPT_P):
            return False
        actual = hashlib.scrypt(password.encode('utf-8'), salt=bytes.fromhex(salt),
                                n=int(n), r=int(r), p=int(p), dklen=32, maxmem=256 * 1024 * 1024)
        return hmac.compare_digest(actual.hex(), expected)
    except (ValueError, TypeError):
        return False


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


class AuthStore:
    def __init__(self, path: str):
        self.path = Path(path).expanduser()
        # StateStore creates learner_states first; the same backup includes all accounts.
        with closing(self.connect()) as connection, connection:
            connection.executescript('''
                CREATE TABLE IF NOT EXISTS accounts (
                    user_id TEXT PRIMARY KEY, email TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL, name TEXT NOT NULL,
                    learner_id TEXT NOT NULL REFERENCES learner_states(learner_id)
                );
                CREATE TABLE IF NOT EXISTS learner_owners (
                    learner_id TEXT PRIMARY KEY REFERENCES learner_states(learner_id),
                    user_id TEXT NOT NULL REFERENCES accounts(user_id)
                );
                CREATE TABLE IF NOT EXISTS auth_sessions (
                    token_hash TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES accounts(user_id),
                    expires_at REAL NOT NULL
                );
                CREATE TABLE IF NOT EXISTS auth_attempts (bucket TEXT NOT NULL, attempted_at REAL NOT NULL);
                CREATE INDEX IF NOT EXISTS auth_attempt_bucket ON auth_attempts(bucket, attempted_at);
            ''')
        self.dummy_password = hash_password(secrets.token_urlsafe(32))

    def connect(self):
        connection = sqlite3.connect(self.path, timeout=10)
        connection.execute('PRAGMA foreign_keys=ON')
        connection.row_factory = sqlite3.Row
        return connection

    def credentials(self, email: str):
        with closing(self.connect()) as connection:
            row = connection.execute('SELECT * FROM accounts WHERE email=?', (email,)).fetchone()
        return dict(row) if row else None

    def create_account(self, email, password_hash, name, learner_id, snapshot):
        user_id, token = str(uuid4()), secrets.token_urlsafe(32)
        with closing(self.connect()) as connection, connection:
            connection.execute('BEGIN IMMEDIATE')
            connection.execute('INSERT INTO learner_states VALUES (?, ?)',
                               (learner_id, snapshot.model_dump_json()))
            connection.execute('INSERT INTO accounts VALUES (?, ?, ?, ?, ?)',
                               (user_id, email, password_hash, name, learner_id))
            connection.execute('INSERT INTO learner_owners VALUES (?, ?)', (learner_id, user_id))
            self._insert_session(connection, user_id, token)
        return token

    def _insert_session(self, connection, user_id, token):
        connection.execute('DELETE FROM auth_sessions WHERE expires_at <= ?', (time.time(),))
        connection.execute('INSERT INTO auth_sessions VALUES (?, ?, ?)',
                           (token_hash(token), user_id, time.time() + SESSION_SECONDS))

    def new_session(self, user_id: str, old_token: str | None = None):
        token = secrets.token_urlsafe(32)
        with closing(self.connect()) as connection, connection:
            if old_token:
                connection.execute('DELETE FROM auth_sessions WHERE token_hash=?', (token_hash(old_token),))
            self._insert_session(connection, user_id, token)
        return token

    def authenticate(self, token: str | None):
        if not token or len(token) > 256:
            return None
        with closing(self.connect()) as connection:
            row = connection.execute('''SELECT a.user_id, a.email, a.name, a.learner_id
                FROM auth_sessions s JOIN accounts a ON a.user_id=s.user_id
                WHERE s.token_hash=? AND s.expires_at>?''', (token_hash(token), time.time())).fetchone()
        return dict(row) if row else None

    def logout(self, token: str | None):
        if not token:
            return
        with closing(self.connect()) as connection, connection:
            connection.execute('DELETE FROM auth_sessions WHERE token_hash=?', (token_hash(token),))

    def owns(self, user_id: str, learner_id: str) -> bool:
        with closing(self.connect()) as connection:
            return connection.execute('SELECT 1 FROM learner_owners WHERE user_id=? AND learner_id=?',
                                      (user_id, learner_id)).fetchone() is not None

    def create_learner(self, user_id, learner_id, snapshot):
        with closing(self.connect()) as connection, connection:
            connection.execute('BEGIN IMMEDIATE')
            connection.execute('INSERT INTO learner_states VALUES (?, ?)', (learner_id, snapshot.model_dump_json()))
            connection.execute('INSERT INTO learner_owners VALUES (?, ?)', (learner_id, user_id))

    def throttle(self, buckets: list[tuple[str, int]], window: int = 900) -> bool:
        now = time.time()
        with closing(self.connect()) as connection, connection:
            connection.execute('BEGIN IMMEDIATE')
            connection.execute('DELETE FROM auth_attempts WHERE attempted_at < ?', (now-window,))
            for bucket, limit in buckets:
                count = connection.execute('SELECT COUNT(*) FROM auth_attempts WHERE bucket=? AND attempted_at>=?',
                                           (bucket, now-window)).fetchone()[0]
                if count >= limit:
                    return False
            connection.executemany('INSERT INTO auth_attempts VALUES (?, ?)', [(bucket, now) for bucket, _ in buckets])
        return True

    def link_legacy(self, email: str, learner_id: str):
        # Local maintenance only. There is intentionally no public claim-by-ID endpoint.
        with closing(self.connect()) as connection, connection:
            connection.execute('BEGIN IMMEDIATE')
            user = connection.execute('SELECT user_id FROM accounts WHERE email=?', (email.strip().casefold(),)).fetchone()
            if not user:
                raise ValueError('Compte introuvable.')
            if not connection.execute('SELECT 1 FROM learner_states WHERE learner_id=?', (learner_id,)).fetchone():
                raise ValueError('Profil introuvable.')
            if connection.execute('SELECT 1 FROM learner_owners WHERE learner_id=?', (learner_id,)).fetchone():
                raise ValueError('Ce profil appartient déjà à un compte.')
            connection.execute('INSERT INTO learner_owners VALUES (?, ?)', (learner_id, user['user_id']))
            connection.execute('UPDATE accounts SET learner_id=? WHERE user_id=?', (learner_id, user['user_id']))
            connection.execute('DELETE FROM auth_sessions WHERE user_id=?', (user['user_id'],))


if __name__ == '__main__':
    import argparse
    from app.config import settings
    from app.persistence import StateStore
    parser = argparse.ArgumentParser(description='Rattacher un profil local ancien à un compte existant (API arrêtée).')
    parser.add_argument('email')
    parser.add_argument('learner_id')
    args = parser.parse_args()
    StateStore(settings.database_path)
    AuthStore(settings.database_path).link_legacy(args.email, args.learner_id)
    print('Profil rattaché. Reconnectez le compte.')

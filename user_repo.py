from psycopg2.extras import DictCursor
from contextlib import contextmanager

class UsersRepository:
    def __init__(self, pool) -> None:
        """
        Принимает объект пула соединений (например, ThreadedConnectionPool)
        """
        self.pool = pool
    
    @contextmanager
    def _get_conn(self, commit=False):
        """
        Вспомогательный контекстный менеджер.
        Автоматически берет соединение из пула и возвращает его обратно.
        """
        conn = self.pool.getconn()
        try:
            yield conn
            if commit:
                conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            self.pool.putconn(conn)
    
    def get_content(self):
        with self._get_conn() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute("SELECT * FROM users ORDER BY id")
                return [dict(row) for row in cur.fetchall()]
        
    def find(self, user_id):
        if not user_id:
            return None
        with self._get_conn() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
                row = cur.fetchone()
                return dict(row) if row else None

    def find_by_email(self, email):
        with self._get_conn() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute("SELECT * FROM users WHERE email = %s", (email,))
                row = cur.fetchone()
                return dict(row) if row else None

    def search(self, query):
        with self._get_conn() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                # ILIKE делает поиск регистронезависимым в Postgres
                cur.execute("SELECT * FROM users WHERE user_name ILIKE %s", (f"%{query}%",))
                return [dict(row) for row in cur.fetchall()]
    
    def create(self, user_data):
        # Передаем commit=True, чтобы изменения сохранились в базе данных
        with self._get_conn(commit=True) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO users (user_name, password, email) VALUES (%s, %s, %s)",
                    (user_data["name"], user_data["password"], user_data["email"])
                )
    
    def update(self, user_id, user_data):
        with self._get_conn(commit=True) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE users SET user_name = %s, password = %s, email = %s WHERE id = %s",
                    (user_data["name"], user_data["password"], user_data["email"], user_id)
                )

    def delete(self, user_id):
        with self._get_conn(commit=True) as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
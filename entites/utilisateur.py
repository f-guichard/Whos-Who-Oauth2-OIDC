import sys
sys.path.insert(1, '../repertoire')

from flask_login import UserMixin

from repertoire.database import get_db

class User(UserMixin):
    def __init__(self, id_, nom, email, avatar):
        self.id = id_
        self.nom = nom
        self.email = email
        self.avatar = avatar

    @staticmethod
    def get(user_id):
        db = get_db()
        user = db.execute(
            "SELECT * FROM utilisateurs WHERE id = ?", (user_id,)
        ).fetchone()
        if not user:
            return None

        user = User(
            id_=user[0], nom=user[1], email=user[2], avatar=user[3]
        )
        return user

    @staticmethod
    def create(id_, nom, email, avatar):
        db = get_db()
        db.execute(
            "INSERT INTO utilisateur (id, nom, email, avatar) "
            "VALUES (?, ?, ?, ?)",
            (id_, nom, email, avatar),
        )
        db.commit()

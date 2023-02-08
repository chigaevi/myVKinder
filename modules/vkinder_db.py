import os
import sqlalchemy
import psycopg2
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

Base = declarative_base()


class user(Base):
    __tablename__ = 'user'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    vk_id_user = sqlalchemy.Column(sqlalchemy.String(length=15), nullable=False)

    def __str__(self):
        return f'id: {self.id}, vk_id: {self.vk_id_user}'


class favorite(Base):
    __tablename__ = 'favorite'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    id_user = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey(user.id), nullable=False)
    name = sqlalchemy.Column(sqlalchemy.String(length=60), nullable=False)
    link = sqlalchemy.Column(sqlalchemy.String(length=100), nullable=False)
    photo_1 = sqlalchemy.Column(sqlalchemy.String(length=100), nullable=True)
    photo_2 = sqlalchemy.Column(sqlalchemy.String(length=100), nullable=True)
    photo_3 = sqlalchemy.Column(sqlalchemy.String(length=100), nullable=True)

    def __str__(self):
        return f'id: {self.id}, victim: {self.id_user}, name: {self.name}'


class block_list(Base):
    __tablename__ = 'block_list'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    id_user = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey(user.id), nullable=False)
    id_blocked_user = sqlalchemy.Column(sqlalchemy.String(length=20), nullable=False)


def create_tables():
    engine = start_engine()
    Base.metadata.create_all(engine)


def drop_tables():
    engine = start_engine()
    Base.metadata.drop_all(engine)


def start_engine():
    db_type = 'postgresql'
    db_login = 'postgres'
    # БД нужно предварительно создать, например для терминала 'createdb -U postgres VKinder_DB'
    db_name = 'VKinder_DB'
    db_host = 'localhost:5432'
    # предварительно прописываем в Environment Variables переменную с именем PAS в значение пароль от БД
    db_pass = os.getenv('PAS')
    DSN = f"{db_type}://{db_login}:{db_pass}@{db_host}/{db_name}"
    engine = sqlalchemy.create_engine(DSN, echo=False, )
    return engine


def add_user(vk_id_user):
    engine = start_engine()
    Session = sessionmaker(bind=engine)
    session = Session()
    item_data = user(vk_id_user=vk_id_user)
    session.add(item_data)
    session.commit()
    # print('user added')
    session.close()


def find_user(vk_id_user=None):
    engine = start_engine()
    Session = sessionmaker(bind=engine)
    session = Session()
    results = session.query(user).filter(user.vk_id_user == vk_id_user).all()
    result_list = []
    for result in results:
        result_list.append(result.id)
    return result_list


def user_exist(vk_id_user):
    engine = start_engine()
    Session = sessionmaker(bind=engine)
    session = Session()
    q = session.query(user).filter(user.vk_id_user == vk_id_user)
    exist = session.query(q.exists()).scalar()
    return exist


def add_favorite(item):  # []
    engine = start_engine()
    Session = sessionmaker(bind=engine)
    session = Session()
    id_user = item[0]
    name = item[1]
    link = item[2]
    photo_list = [None, None, None]
    for ind, photo in enumerate(item[3]):
        photo_list[ind] = photo

    item_data = favorite(
        id_user=id_user,
        link=link,
        name=name,
        photo_1=photo_list[0],
        photo_2=photo_list[1],
        photo_3=photo_list[2],
    )
    session.add(item_data)
    session.commit()
    # print('favorite added')
    session.close()


def veiw_favorites(id_user):
    engine = start_engine()
    Session = sessionmaker(bind=engine)
    session = Session()
    results = session.query(favorite).filter(favorite.id_user == id_user).all()
    result_list = []
    for result in results:
        result_list.append([result.name, result.link])
    return result_list


def favorite_exist(name):
    engine = start_engine()
    Session = sessionmaker(bind=engine)
    session = Session()
    q = session.query(favorite).filter(favorite.name == name)
    exist = session.query(q.exists()).scalar()
    return exist


def add_user_in_blocklist(db_user_id, id_blocked_user):
    engine = start_engine()
    Session = sessionmaker(bind=engine)
    session = Session()
    item_data = block_list(id_user=db_user_id, id_blocked_user=id_blocked_user)
    session.add(item_data)
    session.commit()
    # print('user added in the blocklist')
    session.close()


def user_exists_in_blocklist(id_user, id_blocked_user):
    engine = start_engine()
    Session = sessionmaker(bind=engine)
    session = Session()

    q = session.query(block_list).filter(block_list.id_user == id_user).filter(
        block_list.id_blocked_user == id_blocked_user)
    exist = session.query(q.exists()).scalar()
    # print('user exists in the blocklist - ', exist)
    return exist

import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()

engine = create_engine('postgresql://webadmin:admin2017@localhost/catalog')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))
    created_timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    modified_timestamp = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'picture': self.picture
        }


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(250), unique=True)
    created_timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    modified_timestamp = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.name,
        }


class CategoryItem(Base):
    __tablename__ = 'category_item'

    name = Column(String(250), unique=True, nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(500))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    created_timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    modified_timestamp = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            "category_id": self.category_id,
            'name': self.name,
            'description': self.description,
            'id': self.id,
        }


# User Table helper methods
def getUserID(email):
    """Return the User data that match with the email"""
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except Exception:
        return None


def getUserInfo(user_id):
    """Return the User data that match with the user id"""
    user = session.query(User).filter_by(id=user_id).one()
    return user


def createUser(login_session):
    """Save the new user in the database and return the user id"""
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    createQuery(newUser)
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


# Category Table Helper methods
def getCategories():
    """ Return a list with all categories from the database"""
    categories = session.query(Category).all()
    return categories


def getCategoryByName(category_name):
    """Return the category data that match with the name"""
    category = session.query(Category).filter_by(name=category_name).one()
    return category


def createCategory(data):
    """Save the new category in the database and return the
     the sussess of the process as a bool """
    newCategory = Category(name=data['name'])
    return createQuery(newCategory)


# Category_item Table Helper Methods
def getCategoryItems(category_id):
    """ Return a list with all items related to
    a category id in the database"""
    return session.query(CategoryItem).filter_by(category_id=category_id).all()


def getCategoryItem(category_id, item_name):
    """Return the item data that match with the
    category id and the item name"""
    try:
        return session.query(CategoryItem).filter_by(
            name=item_name).filter_by(category_id=category_id).one()
    except Exception:
        return None


def getLatest10Items():
    """ Return a list with the last 10 items saved in the database"""
    return session.query(CategoryItem).order_by(
        desc(CategoryItem.created_timestamp)).limit(10).all()


def createCategoryItem(data):
    """Save the new item in the database and return the
     the sussess of the process as a bool """
    newCategoryItem = CategoryItem(
        name=data['name'],
        description=data['description'],
        category_id=data['category_id'],
        user_id=data['user_id'],
        )
    return createQuery(newCategoryItem)


def deleteCategoryItem(category_item):
    """delete the  item from the database and return the
     the sussess of the process as a bool """
    return deleteRowQuery(category_item)


# General Helper Methods
def commitUpdate():
    try:
        session.commit()
        return True
    except Exception:
        session.rollback()
        return False


def createQuery(row):
    try:
        session.add(row)
        session.commit()
        return True
    except Exception:
        session.rollback()
        return False


def deleteRowQuery(row):
    try:
        session.delete(row)
        session.commit()
        return True
    except Exception:
        return False


if __name__ == "__main__":
    Base.metadata.create_all(engine)

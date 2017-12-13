from sqlalchemy import Column, ForeignKey, Integer, String
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

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
        }


class CategoryItem(Base):
    __tablename__ = 'category_item'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    price = Column(String(8))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
            'price': self.price,
        }

# User Table helper methods
def getUserID(email):
    try:
        user = session.query(User).filter_by(email = email).one()
        return user.id
    except:
        return None


def getUserInfo(user_id):
    user = session.query(User).filter_by(id = user_id).one()
    return user


def createUser(login_session):
    newUser = User(name = login_session['username'], email =
        login_session['email'], picture = login_session['picture'])
    createQuery(newUser)
    user = session.query(User).filter_by(email = login_session['email']).one()
    return user.id


# Category Table Helper methods
def getCategories():
    categories= session.query(Category).all()
    return categories


def getCategory(category_id):
    category= session.query(Category).filter_by(id = category_id).one()
    return category


def createCategory(data):
    newCategory= Category(name= data['name'], user_id= data['user_id'])
    return createQuery(newCategory)


def editCategory(data):
    try:
        editCategory= getCategory(data['id'])
        editCategory.name= data['name']
        session.commit()
        return True
    except Exception:
        session.rollback()
        return False


def deleteCategory(category):
    items= getCategoryItems(category.id)
    for item in items:
        session.delete(item)
    return deleteRowQuery(category)


#Category_item Table Helper Methods
def getCategoryItems(category_id):
    return session.query(CategoryItem).filter_by(category_id=category_id).all()


def getCategoryItem(item_id):
    return session.query(CategoryItem).filter_by(id=item_id).one()


def createCategoryItem(data):
    newCategoryItem= CategoryItem(
        name= data['name'],
        description= data['description'],
        price= data['price'],
        category_id= data['category_id'],
        user_id= data['user_id'],
        )
    return createQuery(newCategoryItem)


def editCategoryItem(data):
    try:
        editItem= getCategoryItem(data['id'])
        editItem.name= data['name']
        editItem.description= data['description']
        editItem.price= data['price']
        session.commit()
        return True
    except Exception:
        session.rollback()
        return False


def deleteCategoryItem(category_item):
    return deleteRowQuery(category_item)


#General Helper Methods
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
import db_modules

categories = [
    'Displays',
    'Computer parts',
    'Accessories',
    'Laptops',
    'Software'
]


if __name__ == "__main__":
    db_modules.Base.metadata.create_all(db_modules.engine)
    for category in categories:
        data = {'name': category}
        db_modules.createCategory(data)


import shelve

class Book:
    def __init__(self):
        self.__name = ''
        self.__price = 0
        self.__description = ''
        self.__image = ''
        self.__stock = 0
        self.__category = ''



def create_book(name, price, description, imagename, stock, category):
    u = Book()
    u.name = name
    u.price = price
    u.description = description
    u.image = imagename
    u.stock = stock
    u.category = category
    v = shelve.open('test_shelf.db')
    v[name] = { 'name': name, 'price':price, 'description':description, 'image': imagename, 'stock': stock, 'category': category}
    v.sync()
    v.close()
    return u


# retrieve all users
def get_all_books():
    books_list = []
    rec_list = []
    v = shelve.open('test_shelf.db')
    klist = list(v.keys())
    klist.sort()
    print("List:",klist)
    for key in klist:
        print(key)
        print(v[key])
        a = list(v[ key ].values())
        a.insert(0,key)
        print("a", a)
        if a[5] > 0:
            books_list.append(a)
    klist = list(v.keys())
    klist.reverse()
    print("List:",klist)
    for key in klist:
        print(key)
        print(v[key])
        a = list(v[ key ].values())
        a.insert(0,key)
        print("a", a)
        if a[5] > 0:
            rec_list.append(a)
    v.close()
    return books_list, rec_list

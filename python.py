def simple_decorator(func):
    def wrapper():
        print("Действие до вызова функции")
        func()
        print("Действие после вызова функции")
    return wrapper

@simple_decorator
def say_hello():
    print("Привет!")

say_hello()
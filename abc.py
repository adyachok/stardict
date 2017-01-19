

class User():

    static_variable = 6

    def __init__(self, username, email):  # Constructor
        self.username = username  # instance variable
        self.email = email  # instance variable

    def changeEmail(self, new_email):  # Can be use as instance or static method
        self.email = new_email


john = User('john', 'john@email.com')
john.changeEmail('johndoe@email.com')  # Use as instance method

jack = User('Jack', 'Jack@email.com')
User.changeEmail(jack, 'JackBlack@email.com')  # Use as static method with object binding

print(john.static_variable)  # 6 => john instance doesn't has static_variable => look up in User class
john.static_variable = 10  # Create a new instance variable named static_variable
print(User.static_variable)  # 6 => Real static variable
User.static_variable = 5
print(jack.static_variable)  # 5 => jack instance doesn't has static_variable => look up in User class

# Real instance
john.new_instance_variable = 'hello'  # Create new instance new_variable
john.new_instance_method = lambda a, b:a+b  # Create new instance method
john.new_instance_method = min  # assign Math.min function

# Real static
User.new_static_variable = 'new_static_variable'
User.new_static_method = min

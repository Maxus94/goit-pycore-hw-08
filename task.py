from collections import UserDict
from datetime import datetime, timedelta
import re, pickle

class Field:
    def __init__(self, value):
        self.value = value        

    def __str__(self):
        return str(self.value)

class Name(Field):
    # реалізація класу
    def __init__(self, value):
        if value:
            super().__init__(value)
        else:
            print("Name is compulsory")
    

class Phone(Field):
    # реалізація класу
    def __init__(self, value):
        digits = re.findall(r"\d", value)        
        if len(value) == 10 and len(digits) == 10:
            super().__init__(value)            
        else:
            raise ValueError("Phone number must have 10 digits")

class Birthday(Field):
    def __init__(self, value):
        try:
            birthday_date = datetime.strptime(value, "%d.%m.%Y").date()
            super().__init__(birthday_date)
            # Додайте перевірку коректності даних
            # та перетворіть рядок на об'єкт datetime
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
    def __str__(self):        
        return datetime.strftime(self.value, "%d.%m.%Y")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    # реалізація класу
        
    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def add_birthday(self, birthday):
        self.birthday=Birthday(birthday)

    def remove_phone(self, phone):                
        phone_found = False
        for phone_num in self.phones:            
            if phone_num.value == phone:                
                self.phones.remove(phone_num)
                phone_found = True        

        if not phone_found:
            print(f"Phone number {phone} does not exist")

    def edit_phone(self, phone, new_phone):                
        phone_found = False
        for phone_num in self.phones:            
            if phone_num.value == phone:                
                self.phones.remove(phone_num)
                self.phones.append(Phone(new_phone))
                phone_found = True            

        if not phone_found:
            print('Such phone number does not exist')     

    def __str__(self):        
        return f"Contact name: {self.name.value}, Birthday: {self.birthday or "Birthday not added"}, phones: {'; '.join(p.value for p in self.phones)}"

class AddressBook(UserDict):
    # реалізація класу
    def __init__(self):    
        self.data = {}
    
    def add_record(self, record):        
        self.data[record.name.value] = record        
    
    def find(self, name):       
        if name in self.data.keys():
            return(self.data[name])            
        else: 
            return None
    
    def delete(self, name):
        self.data.pop(name)

    def __str__(self):        
        rec='Your address book:\n'
        for name, record in self.items():
            rec = rec + str(record) + '; \n'
        return rec
    
    def get_upcoming_birthdays(self):
        current_date = datetime.today().date()        
        congratulation_dates = []
        for name, record in self.items():                        
            user_birthday_this_year = datetime(year=current_date.year, month=record.birthday.value.month, day=record.birthday.value.day)
            user_birthday_this_year = user_birthday_this_year.date()
            if (current_date.month == 12 and user_birthday_this_year.month == 1):            
                if (current_date.year % 4 == 0):
                    diff_dates = user_birthday_this_year - current_date + timedelta(days = 366)
                else: 
                    diff_dates = user_birthday_this_year - current_date + timedelta(days = 365)
            else:
                diff_dates = user_birthday_this_year - current_date
            diff_dates = diff_dates.days        
            if (diff_dates >= 0) and (diff_dates <= 7):            
                congratulation_date = user_birthday_this_year
                if(user_birthday_this_year.weekday() == 5):
                    congratulation_date = user_birthday_this_year + timedelta(days = 2)
                elif(user_birthday_this_year.weekday() == 6):
                    congratulation_date = user_birthday_this_year + timedelta(days = 1)                                        
                congratulation_date = congratulation_date.strftime("%d.%m.%Y")
                congratulation_dates.append({"name": name, "congratulation_date":congratulation_date})                
        return(congratulation_dates)

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError as e:
            return e.args[0]
        except IndexError as e:
            return e
        except ValueError as e:
            return e
    return inner


def parse_input(user_input):
    try:
        cmd, *args = user_input.split()
        cmd = cmd.strip().lower()
        return cmd, *args
    except:
        return " "    
    
@input_error
def add_contact(args, book: AddressBook):
    try:
        name, phone, *_ = args
    except: raise ValueError("Please, enter Name and phone number")
    record = book.find(name)    
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_contact(args, book: AddressBook):
    try:
        name, phone, new_phone = args
    except:
         raise ValueError("Please, enter name, old phone number and new phone number")        
    if book.find(name):
        book.find(name).edit_phone(phone, new_phone)
    else: 
        raise KeyError(f"Contact with name {name} doesn't exist")
    return "Contact Updated."

@input_error
def phones(args, book: AddressBook):
    try:
        name = args[0]        
    except:
        raise ValueError("Please, enter name")
    if book.find(name):
        user_phones=[]
        for user_phone in book.find(name).phones:
            user_phones.append(user_phone.value)
        return user_phones
    else: 
        raise KeyError(f"Contact with name {name} doesn't exist")
    
@input_error
def add_contact_birthday(args, book: AddressBook):
    try:
        name, birthday = args
    except:
        raise ValueError("Please, enter name and birthday date")            
    if book.find(name):
        book.find(name).add_birthday(birthday)
    else: 
        raise KeyError(f"Contact with name {name} doesn't exist")
    return "Birthday added."

@input_error
def contact_birthday(args, book: AddressBook):
    try:
        name = args[0]  
    except:
        raise ValueError("Please, enter name")          
    if book.find(name):
        return book.find(name).birthday
    else: 
        raise KeyError(f"Contact with name {name} doesn't exist")

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Повернення нової адресної книги, якщо файл не знайдено

def main():
    book = load_data()
    # Основний цикл програми

    
    
    # book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            save_data(book)
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))
            # реалізація

        elif command == "change":
            print(change_contact(args, book))
            # реалізація

        elif command == "phone":
            # реалізація
            phones_list = phones(args, book)
            phones_string = ''
            for phone in phones_list:
                phones_string = phones_string + " " + str(phone)
            print(f"User {args[0]} has phone numbers:{phones_string}")

        elif command == "all":
            adress_book = book if len(book)>0 else "Address book is empty"
            print(adress_book)
            # реалізація

        elif command == "add-birthday":
            print(add_contact_birthday(args, book))
            # реалізація

        elif command == "show-birthday":
            birthday_date = contact_birthday(args, book) or f"Birthday not added for {args[0]}"
            print(birthday_date)
            # реалізація

        elif command == "birthdays":
            # реалізація
            week_birthdays = book.get_upcoming_birthdays() if len(book.get_upcoming_birthdays()) > 0 else "There is no birthdays during next 7 days"
            print(week_birthdays)

        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
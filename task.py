from datetime import datetime, timedelta
import pickle

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value):
        if not value.strip() or not value.replace(" ", "").isalpha():
            raise ValueError("Name must contain only letters and cannot be empty.")
        super().__init__(value)

class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must contain 10 digits.")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone, new_phone):
        for p in self.phones:
            if p.value == old_phone:
                p.value = Phone(new_phone).value

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p

    def __str__(self):
        phones_str = "; ".join(str(p) for p in self.phones)
        birthday_str = f", birthday: {self.birthday}" if self.birthday else ""
        return f"Contact name: {self.name}, phones: {phones_str}{birthday_str}"

class AddressBook:
    def __init__(self):
        self.data = {}

    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self, days=7):
        today = datetime.today().date()
        upcoming_birthdays = []
        for record in self.data.values():
            if record.birthday:
                birthday_this_year = record.birthday.value.replace(year=today.year)
                if today <= birthday_this_year <= today + timedelta(days=days):
                    upcoming_birthdays.append(record)
        return upcoming_birthdays

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Повернення нової адресної книги, якщо файл не знайдено

def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return str(e)
        except IndexError:
            return "Insufficient arguments provided."
    return wrapper

@input_error
def add_contact(args, book: AddressBook):
    if len(args) < 2:
        return "Please provide a name and a phone number."
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    record.add_phone(phone)
    return message

@input_error
def add_birthday(args, book):
    if len(args) < 2:
        return "Please provide a name and a birthday."
    name, birthday, *_ = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return f"Birthday added to contact {name}."
    return "Contact not found."

@input_error
def show_birthday(args, book):
    if len(args) < 1:
        return "Please provide a name."
    name, *_ = args
    record = book.find(name)
    if record and record.birthday:
        return f"{name}'s birthday is {record.birthday.value.strftime('%d.%m.%Y')}."
    return "Contact not found or birthday not set."

@input_error
def birthdays(args, book):
    upcoming_birthdays = book.get_upcoming_birthdays()
    if not upcoming_birthdays:
        return "No birthdays in the next week."
    result = "Upcoming birthdays:\n"
    for record in upcoming_birthdays:
        result += f"{record.name}: {record.birthday.value.strftime('%d.%m.%Y')}\n"
    return result

def parse_input(user_input):
    parts = user_input.split()
    command = parts[0].lower() if parts else ""
    args = parts[1:]
    return command, args

def main():
    book = load_data()  # Завантаження даних з файлу при запуску

    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        if not user_input.strip():
            print("Please enter a command.")
            continue
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            save_data(book)  # Збереження даних у файл перед виходом
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            if len(args) < 2:
                print("Please provide a name and a new phone number.")
                continue
            name, new_phone, *_ = args
            record = book.find(name)
            if record:
                try:
                    record.edit_phone(record.phones[0].value, new_phone)
                    print(f"Phone number for {name} updated.")
                except ValueError as e:
                    print(str(e))
            else:
                print("Contact not found.")

        elif command == "phone":
            if len(args) < 1:
                print("Please provide a name.")
                continue
            name, *_ = args
            record = book.find(name)
            if record:
                print(f"{name}'s phone number(s): {', '.join(phone.value for phone in record.phones)}")
            else:
                print("Contact not found.")

        elif command == "all":
            for name, record in book.data.items():
                print(record)

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()

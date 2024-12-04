from collections import UserDict
import re
from datetime import datetime, timedelta
import pickle
from abc import ABC, abstractmethod


class UserView(ABC):
    @abstractmethod
    def show_message(self, message):
        pass


    @abstractmethod
    def show_contacts(self, contacts):
        pass


    @abstractmethod
    def show_birthday(self, birthday):
        pass


class ConsoleView(UserView):
    def show_message(self, message):
        print(message)


    def show_contacts(self, contacts):
        for contact in contacts:
            print(f"Name: {contact['name']}, Phone: {contact['phones']}, Birthday: {contact['birthday']}")


    def show_birthday(self, birthdays):
        for birthday in birthdays:
            print(f"Name: {birthday['name']}, Birthday: {birthday['birthday']}")


class Field:
    def __init__(self, value) -> None:
        self.value = value


    def __str__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, value):
        if len(value) != 0:
            super().__init__(value)
        else:
            raise ValueError("Name cannot be empty")


class Phone(Field):
    def __init__(self, number):
        if self.validate_number(number):
            super().__init__(number)
        else:
            raise ValueError("Invalid phone number")


    def validate_number(self, number):
        return len(number) == 10 and re.match(r"^\d+$", number)


    def __eq__(self, other: object) -> bool:
        if isinstance(other, Phone):
            return self.value == other.value
        return False


    def __repr__(self):
        return self.value


class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, '%d.%m.%Y').date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None


    def add_phone(self, phone_number):
        number = Phone(phone_number)
        self.phones.append(number)


    def remove_phone(self, phone_number):
        phone_obj = Phone(phone_number)
        for obj in self.phones:
            if obj == phone_obj:
                self.phones.remove(obj)
                break


    def edit_phone(self, old_number, new_number):
        self.remove_phone(old_number)
        self.add_phone(new_number)


    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        else:
            raise ValueError("Phone number not found")


    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)


    def __repr__(self):
        return f"Record(name={self.name}, phones={self.phones}, birthday={self.birthday})"


class AddressBook(UserDict):
    def add_record(self, record_item):
        self.data[record_item.name.value] = record_item


    def find(self, key):
        if key in self:
            return self[key]
        else:
            raise KeyError("Record not found")


    def delete_record(self, name):
        if name in self.data:
            del self.data[name]
            return f"Contact {name} deleted"
        else:
            return f"Contact {name} not found"


    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        upcoming_birthdays = []
        for record in self.data.values():
            if record.birthday:
                next_birthday = record.birthday.value.replace(year=today.year)
                if today <= next_birthday <= today + timedelta(days=7):
                    upcoming_birthdays.append({
                        'name': record.name.value,
                        'birthday': next_birthday.strftime('%d.%м.%Y')
                    })
        return upcoming_birthdays


def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return f"ValueError: {e}"
        except KeyError as e:
            return f"KeyError: {e}"
        except IndexError:
            return "IndexError: Invalid input, please try again."
        except Exception as e:
            return f"An unexpected error occurred: {e}"
    return wrapper


@input_error
def add_contact(args, address_book):
    name, phone = args
    record = Record(name)
    record.add_phone(phone)
    address_book.add_record(record)
    return f"Contact {name} added with phone number {phone}"


@input_error
def change_phone(args, address_book):
    name, old_phone, new_phone = args
    record = address_book.find(name)
    record.edit_phone(old_phone, new_phone)
    return f"Phone number for {name} changed from {old_phone} to {new_phone}"


@input_error
def show_phones(args, address_book):
    name = args[0]
    record = address_book.find(name)
    return f"{name}'s phones: {', '.join(str(phone) for phone in record.phones)}"


@input_error
def add_birthday(args, address_book):
    name, birthday = args
    record = address_book.find(name)
    record.add_birthday(birthday)
    return f"Birthday for {name} added."


@input_error
def show_all_contacts(address_book, view):
    contacts = []
    for record in address_book.values():
        phones = ', '.join(str(phone) for phone in record.phones)
        birthday = record.birthday.value.strftime('%d.%m.%Y') if record.birthday else "No birthday"
        contacts.append({"name": record.name.value, "phones": phones, "birthday": birthday})
    view.show_contacts(contacts)


@input_error
def show_upcoming_birthdays(address_book, view):
    upcoming_birthdays = address_book.get_upcoming_birthdays()

    if upcoming_birthdays:
        view.show_birthday(upcoming_birthdays)
    else:
        view.show_message("No upcoming birthdays in the next 7 days.")


def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)


def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()


def show_help():
    commands = [
        "hello, hi, hey - Приветствие",
        "add <name> <phone> - Добавить контакт",
        "change <name> <old_phone> <new_phone> - Изменить номер телефона",
        "phone <name> - Показать номера телефонов контакта",
        "all - Показать все контакты",
        "delete <name> - Удалить контакт",
        "add-birthday <name> <birthday> - Добавить день рождения",
        "show-birthday <name> - Показать день рождения контакта",
        "birthdays - Показать ближайшие дни рождения",
        "close, exit - Выйти из программы"
    ]
    return "\n".join(commands)


def main():
    book = load_data()
    view = ConsoleView()

    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ").strip()
        command, *args = user_input.split()
        command = command.lower()

        try:
            if command in ["close", "exit"]:
                save_data(book)
                view.show_message("Good bye!")
                break

            elif command in ["hello", "hi", "hey"]:
                view.show_message("How can I help you?")

            elif command == "add":
                view.show_message(add_contact(args, book))

            elif command == "change":
                view.show_message(change_phone(args, book))

            elif command == "phone":
                view.show_message(show_phones(args, book))

            elif command == "all":
                show_all_contacts(book, view)

            elif command == "delete":
                if args:
                    name = args[0]
                    view.show_message(book.delete_record(name))
                else:
                    view.show_message("Please provide the name of the contact to delete.")

            elif command == "add-birthday":
                view.show_message(add_birthday(args, book))

            elif command == "show-birthday":
                if args:
                    name = args[0]
                    record = book.data.get(name)
                    if record and record.birthday:
                        view.show_message(f"{name}'s birthday is {record.birthday.value.strftime('%d.%m.%Y')}")
                    else:
                        view.show_message(f"No birthday found for {name}.")
                else:
                    view.show_message("Please provide the contact name.")

            elif command == "birthdays":
                show_upcoming_birthdays(book, view)

            elif command == "help":
                view.show_message(show_help())

            else:
                view.show_message("Invalid command.")
        except Exception as e:
            view.show_message(f"An error occurred: {e}")

if __name__ == "__main__":
    main()


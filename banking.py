# bankingprogram.py - A banking program that allows you to create an account,
# and login with that account in order to access bank related information

import random
import math
import sqlite3

conn = sqlite3.connect("card.s3db")
cur = conn.cursor()


def create_num():
    card_num = "400000" + str(random.randint(100000000, 999999999))
    num_lst = [int(x) for x in card_num]
    checksum_lst = []
    for i in range(len(num_lst)):
        if i % 2 == 0:
            even_dbl = num_lst[i] * 2  # Zero-indexing causes the evens to need to be doubled rather than odd
            if even_dbl <= 9:
                checksum_lst.append(even_dbl)
            else:
                checksum_lst.append(even_dbl - 9)
        else:
            checksum_lst.append(num_lst[i])
    checksum = int(math.ceil(sum(checksum_lst) / 10) * 10) - sum(checksum_lst)
    card_num += str(checksum)

    card_pin = str(random.randint(1000, 9999))
    print(f"""
Your card has been created
Your card number:
{card_num}
Your card PIN:
{card_pin}
""")
    card_numbers = [card_num, card_pin]
    sql_card_db(card_numbers)
    return card_numbers


def login_verify():
    card_verify = input("\nEnter your card number:\n")
    pin_verify = input("Enter your PIN:\n")
    cur.execute("SELECT number FROM card")
    card_nums = cur.fetchall()
    cur.execute("SELECT pin FROM card")
    card_pins = cur.fetchall()

    if (card_verify,) in card_nums and (pin_verify,) in card_pins:
        print("\nYou have successfully logged in!")
        return inner_process(card_verify, pin_verify, card_nums)

    else:
        print("Wrong card number or PIN!")
        return main_screen()


def main_screen():
    while True:
        selection = input("""\nPlease select one of the following:
1. Create an account 
2. Log into account
0. Exit\n
""")
        if selection == "1":
            create_num()

        elif selection == "2":
            login_verify()
            break

        elif selection == "0":
            print("\nBye!")
            conn.close()
            break


def inner_process(card_num, card_pin, card_nums):
    inner_choice = input("""\nPlease select one of the following:
1. Balance
2. Add income
3. Do transfer
4. Close account
5. Log out
0. Exit\n
""")
    cur.execute("SELECT balance FROM card WHERE number = ?", (card_num,))
    card_balance = cur.fetchone()
    card_balance = card_balance[0]
    if inner_choice == "1":
        print(f"\nBalance: {card_balance}")
        return inner_process(card_num, card_pin, card_nums)

    elif inner_choice == "2":
        income = int(input("Enter income:\n"))
        cur.execute("UPDATE card SET balance = balance + ? WHERE number = ?", (income, card_num))
        conn.commit()
        return inner_process(card_num, card_pin, card_nums)

    elif inner_choice == "3":
        print("Transfer")
        print(card_nums)
        transfer_to_num = input("Enter card number:\n")

        num_lst = [int(x) for x in transfer_to_num]    # Uses Luhn algorithm to verify the card was written correctly
        checksum_lst = []
        for i in range(len(num_lst) - 1):
            if i % 2 == 0:
                even_dbl = num_lst[i] * 2
                if even_dbl <= 9:
                    checksum_lst.append(even_dbl)
                else:
                    checksum_lst.append(even_dbl - 9)
            else:
                checksum_lst.append(num_lst[i])
        checksum = int(math.ceil(sum(checksum_lst) / 10) * 10) - sum(checksum_lst)

        if transfer_to_num == card_num:
            print("You can't transfer money to the same account!")
            return inner_process(card_num, card_pin, card_nums)

        elif transfer_to_num[-1] != str(checksum):
            print("Probably you made mistake in the card number. Please try again!")
            return inner_process(card_num, card_pin, card_nums)

        elif (transfer_to_num,) not in card_nums:
            print("Such a card does not exist.")
            return inner_process(card_num, card_pin, card_nums)

        elif (transfer_to_num,) in card_nums:   # NEEDS FIXED
            transfer_amt = int(input("Enter how much money you want to transfer:\n"))
            if transfer_amt < card_balance:
                cur.execute("UPDATE card SET balance = ? WHERE number = ?", (transfer_amt, transfer_to_num))
                cur.execute("UPDATE card set balance = ? WHERE number = ?", (card_balance - transfer_amt, card_num))
                conn.commit()
                print("Success!")
                return inner_process(card_num, card_pin, card_nums)
            else:
                print("Not enough money!")
                return inner_process(card_num, card_pin, card_nums)

    elif inner_choice == "4":
        cur.execute("DELETE FROM card WHERE number = ?", (card_num,))
        conn.commit()
        print("The account has been closed!")
        return main_screen()

    elif inner_choice == "5":
        print("\nYou have successfully logged out!")
        return main_screen()

    elif inner_choice == "0":
        print("\nBye!")
        conn.close()
        return None


def sql_card_db(card_numbers):
    cur.execute("""
            CREATE TABLE IF NOT EXISTS card(
            id INTEGER PRIMARY KEY,
            number TEXT,
            pin TEXT,
            balance INTEGER DEFAULT 0
            );
    """)

    cur.execute("INSERT INTO card(number, pin) VALUES (?, ?)", (card_numbers[0], card_numbers[1]))
    conn.commit()

    cur.execute("SELECT * FROM card WHERE id=(SELECT max(id) FROM card)")
    my_result = cur.fetchall()
    print(my_result)


main_screen()

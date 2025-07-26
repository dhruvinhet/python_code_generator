# main.py

from bank import Bank

def main():
    """Main function to run the bank account simulator."""
    bank = Bank()

    while True:
        print("\nBank Account Simulator")
        print("1. Create Account")
        print("2. Deposit")
        print("3. Withdraw")
        print("4. Check Balance")
        print("5. View Transaction History")
        print("6. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            account_holder = input("Enter account holder's name: ")
            initial_deposit = float(input("Enter initial deposit amount (or 0 for none): "))
            account_number = bank.create_account(account_holder, initial_deposit)
            print(f"Account created successfully. Account number: {account_number}")

        elif choice == '2':
            account_number = input("Enter account number: ")
            amount = float(input("Enter deposit amount: ")
                           )
            if bank.perform_transaction(account_number, 'deposit', amount):
                print("Deposit successful.")
            else:
                print("Deposit failed.")

        elif choice == '3':
            account_number = input("Enter account number: ")
            amount = float(input("Enter withdrawal amount: "))
            if bank.perform_transaction(account_number, 'withdrawal', amount):
                print("Withdrawal successful.")
            else:
                print("Withdrawal failed.")

        elif choice == '4':
            account_number = input("Enter account number: ")
            account = bank.get_account(account_number)
            if account:
                print(f"Account balance: ${account.get_balance()}")
            else:
                print("Account not found.")

        elif choice == '5':
            account_number = input("Enter account number: ")
            history = bank.get_transaction_history(account_number)
            if history:
                print("Transaction History:")
                for transaction in history:
                    print(transaction)
            else:
                print("No transaction history found for this account.")

        elif choice == '6':
            print("Exiting...")
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
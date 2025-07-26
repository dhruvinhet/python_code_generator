# bank.py

from account import BankAccount
from transaction import Transaction

class Bank:
    """Manages multiple bank accounts."""

    def __init__(self):
        """Initializes a Bank object with an empty dictionary of accounts."""
        self.accounts = {}

    def create_account(self, account_holder, initial_balance=0):
        """Creates a new bank account.

        Args:
            account_holder (str): The name of the account holder.
            initial_balance (float): The initial balance of the account. Defaults to 0.

        Returns:
            str: The account number of the newly created account.
        """
        account_number = self._generate_account_number()
        account = BankAccount(account_number, account_holder, initial_balance)
        self.accounts[account_number] = account
        return account_number

    def get_account(self, account_number):
        """Retrieves a bank account by its account number.

        Args:
            account_number (str): The account number to retrieve.

        Returns:
            BankAccount: The BankAccount object, or None if the account is not found.
        """
        return self.accounts.get(account_number)

    def perform_transaction(self, account_number, transaction_type, amount):
        """Performs a transaction on a bank account.

        Args:
            account_number (str): The account number to perform the transaction on.
            transaction_type (str): The type of transaction ('deposit' or 'withdrawal').
            amount (float): The amount to deposit or withdraw.

        Returns:
            bool: True if the transaction was successful, False otherwise.

        Raises:
            ValueError: If the transaction type is invalid or if the deposit/withdrawal fails.
        """
        account = self.get_account(account_number)
        if not account:
            print("Account does not exist.")
            return False

        try:
            if transaction_type == 'deposit':
                if account.deposit(amount):
                    transaction = Transaction(transaction_type, amount)
                    self.transaction_history.setdefault(account_number, []).append(transaction)
                    return True
            elif transaction_type == 'withdrawal':
                if account.withdraw(amount):
                    transaction = Transaction(transaction_type, amount)
                    self.transaction_history.setdefault(account_number, []).append(transaction)
                    return True
            else:
                raise ValueError("Invalid transaction type")
        except ValueError as e:
            print(f"Transaction failed: {e}")
            return False

    def get_transaction_history(self, account_number):
        """Retrieves the transaction history for a given account.

        Args:
            account_number (str): The account number to retrieve the history for.

        Returns:
            list: A list of Transaction objects representing the transaction history.
        """
        return self.transaction_history.get(account_number, [])

    def _generate_account_number(self):
        """Generates a unique account number (simple implementation)."""
        import uuid
        return str(uuid.uuid4())

    def __init__(self):
        self.accounts = {}
        self.transaction_history = {}

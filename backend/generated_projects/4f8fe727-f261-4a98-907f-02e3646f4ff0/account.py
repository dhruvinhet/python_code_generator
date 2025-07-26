# account.py

class BankAccount:
    """Represents a bank account with basic operations."""

    def __init__(self, account_number, account_holder, initial_balance=0):
        """Initializes a BankAccount object.

        Args:
            account_number (str): The unique account number.
            account_holder (str): The name of the account holder.
            initial_balance (float): The initial balance of the account. Defaults to 0.

        Raises:
            ValueError: If the initial balance is negative.
        """
        if initial_balance < 0:
            raise ValueError("Initial balance cannot be negative")

        self.account_number = account_number
        self.account_holder = account_holder
        self.balance = initial_balance

    def deposit(self, amount):
        """Deposits money into the account.

        Args:
            amount (float): The amount to deposit.

        Raises:
            ValueError: If the deposit amount is negative.
        """
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self.balance += amount
        return True  # Indicate success

    def withdraw(self, amount):
        """Withdraws money from the account.

        Args:
            amount (float): The amount to withdraw.

        Raises:
            ValueError: If the withdrawal amount is negative or exceeds the balance.
        """
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if amount > self.balance:
            raise ValueError("Insufficient balance")
        self.balance -= amount
        return True  # Indicate success

    def get_balance(self):
        """Returns the current balance of the account.

        Returns:
            float: The current balance.
        """
        return self.balance

    def get_account_number(self):
        """Returns the account number.

        Returns:
            str: The account number.
        """
        return self.account_number

    def get_account_holder(self):
        """Returns the account holder's name.

        Returns:
            str: The account holder's name.
        """
        return self.account_holder
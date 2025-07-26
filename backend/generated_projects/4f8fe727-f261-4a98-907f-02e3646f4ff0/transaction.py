# transaction.py

from datetime import datetime

class Transaction:
    """Represents a bank transaction."""

    def __init__(self, transaction_type, amount, timestamp=None):
        """Initializes a Transaction object.

        Args:
            transaction_type (str): The type of transaction (e.g., 'deposit', 'withdrawal').
            amount (float): The amount involved in the transaction.
            timestamp (datetime): The timestamp of the transaction. Defaults to current time.
        """
        self.transaction_type = transaction_type
        self.amount = amount
        self.timestamp = timestamp if timestamp else datetime.now()

    def __str__(self):
        """Returns a string representation of the transaction.

        Returns:
            str: A formatted string representing the transaction.
        """
        return f"{self.timestamp}: {self.transaction_type} - ${self.amount}"
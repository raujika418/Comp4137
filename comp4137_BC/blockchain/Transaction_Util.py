import hashlib
import json
import random
import string


class TransactionInput(object):
    """
    An input for a transaction. This points to an output of another transaction
    """

    def __init__(self, transaction, output_index):
        self.transaction = transaction
        self.output_index = output_index

    def to_dict(self):
        d = {
            'transaction': self.transaction,
            'output_index': self.output_index
        }
        return d


class TransactionOutput(object):
    """
    An output for a transaction. This specifies an amount and a recipient (wallet)
    """

    def __init__(self, recipient_address, amount):
        self.recipient = recipient_address
        self.amount = amount

    def to_dict(self):
        d = {
            'recipient_address': self.recipient,
            'amount': self.amount
        }
        return d


def compute_fee(inputs, outputs):
    """
    Compute the transaction fee by computing the difference between total input and total output
    """
    total_in = sum(
        i.transaction.outputs[i.output_index].amount for i in inputs)
    total_out = sum(o.amount for o in outputs)
    assert total_out <= total_in, "Invalid transaction with out(%f) > in(%f)" % (
        total_out, total_in)
    return total_in - total_out


def random_string(length=10):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))


class Transaction(object):
    def __init__(self, inputs, outputs):
        """
        Create a transaction spending money from the provided wallet
        """
        self.inputs = inputs
        self.outputs = outputs
        self.id = hash(self)
        self.salt = random_string()

    def to_dict(self):
        d = {
            "inputs": list(map(TransactionInput.to_dict, self.inputs)),
            "outputs": list(map(TransactionOutput.to_dict, self.outputs)),
            "salt": self.salt  # it will avoid same hash if same content transaction
        }
        return d

    def hash(self):
        return sha256(json.dumps(self.to_dict()))


def sha256(message):
    return hashlib.sha256(message.encode('ascii')).hexdigest()


class GenesisTransaction(Transaction):
    """
    This is the first transaction which is a special transaction
    with no input and 25 bitcoins output
    """

    def __init__(self, recipient_address, amount=50):
        super().__init__([],[
            TransactionOutput(recipient_address, amount)
        ])

    def to_dict(self):
        return super().to_dict()

# models/customer.py

class Customer:
    """
    Represents a customer in the PharmaCare system.
    """
    def __init__(self, customer_id=None, name=None, phone=None, email=None, address=None, created_at=None):
        self.id = customer_id
        self.name = name
        self.phone = phone
        self.email = email
        self.address = address
        self.created_at = created_at

    @classmethod
    def from_db_row(cls, row):
        """
        Creates a Customer object from a database row (tuple).
        Assumes row format: (id, name, phone, email, address, created_at)
        """
        if not row:
            return None
        return cls(
            customer_id=row[0],
            name=row[1],
            phone=row[2],
            email=row[3],
            address=row[4],
            created_at=row[5]
        )

    def __repr__(self):
        return (f"Customer(ID={self.id}, Name='{self.name}', Phone='{self.phone}', "
                f"Email='{self.email}', Address='{self.address}', CreatedAt='{self.created_at}')")

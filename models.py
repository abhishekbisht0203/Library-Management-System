from sqlalchemy import Column, Integer, String, Date, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from database import Base
import uuid
from sqlalchemy.sql.expression import text

class Authors(Base):
    __tablename__ = "authors"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    date_of_birth = Column(Date, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default="NOW()")

    books = relationship("Books", back_populates="author")

class Books(Base):
    __tablename__ = "books"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String, nullable=False)
    author_id = Column(UUID(as_uuid=True), ForeignKey("authors.id"), nullable=False)
    author = relationship("Authors", back_populates="books")
    published_date = Column(Date, nullable=False)
    isbn = Column(String, nullable=False, unique=True)
    quantity = Column(Integer, nullable=False)
    available_copies = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default="NOW()")

    transactions = relationship("Transactions", back_populates="book")

class Borrowers(Base):
    __tablename__ = "borrowers"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    membership_date = Column(Date, nullable=False)
    phone_number = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default="NOW()")

    transactions = relationship("Transactions", back_populates="borrower")

class Transactions(Base):
    __tablename__ = "transactions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    borrower_id = Column(UUID(as_uuid=True), ForeignKey("borrowers.id"), nullable=False)
    borrower = relationship("Borrowers", back_populates="transactions")
    book_id = Column(UUID(as_uuid=True), ForeignKey("books.id"), nullable=False)
    book = relationship("Books", back_populates="transactions")
    transaction_type = Column(String, nullable=False, server_default=text("BORROW") )
    transaction_date = Column(TIMESTAMP(timezone=True), nullable=False, server_default="NOW()")
    due_date = Column(Date,nullable=False)
    return_date = Column(TIMESTAMP(timezone=True))
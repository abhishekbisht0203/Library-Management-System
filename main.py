from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from models import Authors, Books, Borrowers, Transactions
from database import get_db
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from datetime import date
from uuid import UUID
from typing import Optional, List
from fastapi.responses import RedirectResponse


app = FastAPI()

class Author(BaseModel):
    id: str
    name: str
    email: str
    date_of_birth: date
    created_at: datetime
    
    class Config:
        from_attributes = True
        
        json_encoders = {
            UUID: str  
        }
        
class Book(BaseModel):
    id: str
    title: str
    author_id: str
    author: Author
    published_date: date
    isbn: str
    quantity: int
    available_copies: int
    created_at: datetime
    
    class Config:
        from_attributes = True
        
        json_encoders = {
            UUID: str  
        }
       
        
class Borrower(BaseModel):
    id: str
    name: str
    email: str
    membership_date: date
    phone_number: str
    created_at: datetime
    
    class Config:
        from_attributes = True
        
        json_encoders = {
            UUID: str  
        }
        
class Transaction(BaseModel):
    id: str
    borrower_id: str
    borrower: Borrower
    book_id: str
    book: Book
    transaction_type: str
    transaction_date: datetime
    due_date: date
    return_date: date
    
    class Config:
        from_attributes = True
        
        json_encoders = {
            UUID: str  
        }


templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def authors(request: Request):
    return templates.TemplateResponse("authors.html", {"request": request})

@app.post("/authors", response_class=HTMLResponse)
async def create_author(request: Request, name: str = Form(...), email: str = Form(...), date_of_birth: str = Form(...), created_at: str = Form(...), db: Session = Depends(get_db)):
    if db.query(Authors).filter(Authors.email == email).first():
        raise HTTPException(status_code=400, detail="Email already exists")
    author = Authors(name=name, email=email, date_of_birth=date_of_birth, created_at=created_at)
    db.add(author)
    db.commit()
    db.refresh(author)
    return templates.TemplateResponse("authors.html", {"request": request})

@app.get('/get_authors', response_model=list[Author])
async def get_all_authors(db: Session = Depends(get_db)):
    authors = db.query(Authors).all()
    for author in authors:
        author.id = str(author.id)
    return authors

@app.get('/get_author/{id}', response_model=Author)
async def get_author(id: UUID, db: Session = Depends(get_db)):
    author = db.query(Authors).filter(Authors.id == id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    author.id = str(author.id)
    return author

@app.get("/books", response_class=HTMLResponse)
async def books(request: Request, db: Session = Depends(get_db)):
    authors = db.query(Authors).all()
    return templates.TemplateResponse("books.html", {"request": request, "authors": authors})  

@app.post("/books", response_class=HTMLResponse)
async def create_books(request: Request, title : str = Form(...), author_id: str = Form(...), published_date: str = Form(...), isbn: str = Form(...), quantity: int = Form(...), available_copies: int = Form(...), created_at: str = Form(...), db: Session = Depends(get_db)):
    if db.query(Books).filter(Books.isbn == isbn).first():
        raise HTTPException(status_code=400, detail="ISBN already exists")
    author = db.query(Authors).filter(Authors.id == author_id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    book = Books(title=title, author_id=author_id, published_date=published_date, isbn=isbn, quantity=quantity, available_copies=available_copies, created_at=created_at)
    db.add(book)
    db.commit()
    db.refresh(book)
    return templates.TemplateResponse("books.html", {"request": request})


@app.get('/get_books', response_model=List[Book])
async def get_books(db: Session = Depends(get_db)):
    books = db.query(Books).all()
    for book in books:
        book.id = str(book.id)
        book.author_id = str(book.author_id)  
        book.author.id = str(book.author.id)  
    return books

@app.get('/get_book/{id}', response_model=Book)
async def get_book(id: UUID, db: Session = Depends(get_db)):
    book = db.query(Books).filter(Books.id == id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    book.id = str(book.id)
    book.author_id = str(book.author_id)  
    book.author.id = str(book.author.id)  
    return book



@app.get("/borrowers", response_class=HTMLResponse)
async def borrowers(request: Request):
    return templates.TemplateResponse("borrowers.html", {"request": request})


@app.post("/borrowers", response_class=HTMLResponse)
async def create_borrower(request: Request,name: str = Form(...),email: str = Form(...),phone_number: str = Form(...),created_at: Optional[str] = Form(None),membership_date: Optional[str] = Form(None),db: Session = Depends(get_db)):
    if db.query(Borrowers).filter(Borrowers.email == email).first():
        raise HTTPException(status_code=400, detail="Email already exists")
     
    membership_date = membership_date or datetime.today().date()
    created_at = created_at or datetime.now().isoformat()
    
    borrower = Borrowers(name=name,email=email,phone_number=phone_number,membership_date=membership_date,created_at=created_at)
    db.add(borrower)
    db.commit()
    db.refresh(borrower)
    
    return templates.TemplateResponse("borrowers.html", {"request": request})

@app.get('/get_borrowers', response_model=list[Borrower])
async def get_all_borrowers(db: Session = Depends(get_db)):
    borrowers = db.query(Borrowers).all()
    for borrower in borrowers:
        borrower.id = str(borrower.id)
    return borrowers

@app.get('/get_borrower/{id}', response_model=Borrower)
async def get_borrower(id: UUID, db: Session = Depends(get_db)):
    borrower = db.query(Borrowers).filter(Borrowers.id == id).first()
    if not borrower:
        raise HTTPException(status_code=404, detail="Borrower not found")
    borrower.id = str(borrower.id)
    return borrower

@app.get("/transactions", response_class=HTMLResponse)
async def transactions(request: Request, db: Session = Depends(get_db)):
    books = db.query(Books).all()
    borrowers = db.query(Borrowers).all()
    return templates.TemplateResponse("transactions.html", {"request": request, "books": books, "borrowers": borrowers})


@app.post("/transactions", response_class=HTMLResponse)
async def create_transaction(request: Request, book_id: str = Form(...), borrower_id: str = Form(...),transaction_type: str = Form(...), transaction_date: str = Form(...), due_date: str = Form(...), return_date: str = Form(...),  db: Session = Depends(get_db)):
    book = db.query(Books).filter(Books.id == UUID(book_id)).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    borrower = db.query(Borrowers).filter(Borrowers.id == UUID(borrower_id)).first()
    if not borrower:
        raise HTTPException(status_code=404, detail="Borrower not found")

    transaction = Transactions(book_id=UUID(book_id), borrower_id=UUID(borrower_id), transaction_type=transaction_type, transaction_date=transaction_date, due_date=due_date, return_date=return_date)
    transactions = db.query(Transactions).all()
    db.add(transaction)
    db.commit() 
    db.refresh(transaction)
    return templates.TemplateResponse("transactions.html", {"request": request, "transactions": transactions})

@app.get('/get_transactions', response_model=list[Transaction])
async def get_all_transactions(db: Session = Depends(get_db)):
    transactions = db.query(Transactions).all()
    for transaction in transactions:
        
        transaction.id = str(transaction.id)
        transaction.book_id = str(transaction.book_id)
        transaction.borrower_id = str(transaction.borrower_id)

        
        transaction.book.id = str(transaction.book.id)
        transaction.book.author_id = str(transaction.book.author_id)

        
        transaction.book.author.id = str(transaction.book.author.id)

        
        transaction.borrower.id = str(transaction.borrower.id)

    return transactions

@app.get('/get_transaction/{id}', response_model=Transaction)
async def get_transaction(id: UUID, db: Session = Depends(get_db)):
    transaction = db.query(Transactions).filter(Transactions.id == id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    transaction.id = str(transaction.id)
    transaction.book_id = str(transaction.book_id)
    transaction.borrower_id = str(transaction.borrower_id)

   
    transaction.book.id = str(transaction.book.id)
    transaction.book.author_id = str(transaction.book.author_id)

    transaction.book.author.id = str(transaction.book.author.id)

  
    transaction.borrower.id = str(transaction.borrower.id)

    return transaction

@app.get('/borrowers/{id}/transactions', response_model=list[Transaction])
async def get_borrower_transactions(id: UUID, db: Session = Depends(get_db)):
    
    transactions = db.query(Transactions).filter(Transactions.borrower_id == id).all()
    
    if not transactions:
        raise HTTPException(status_code=404, detail="No transactions found for this borrower.")

    
    for transaction in transactions:
        transaction.id = str(transaction.id)
        transaction.book_id = str(transaction.book_id)
        transaction.borrower_id = str(transaction.borrower_id)
        transaction.book.id = str(transaction.book.id)
        transaction.book.author_id = str(transaction.book.author_id)
        transaction.book.author.id = str(transaction.book.author.id)
        transaction.borrower.id = str(transaction.borrower.id)

    return transactions
    




               
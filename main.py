import sqlite3
import typer
from rich.console import Console
from typing import Optional
from datetime import datetime
from datetime import date
from getpass import getuser

# Establish connection to SQLite database
conn = sqlite3.connect("sample")
cursor = conn.cursor()

# Initialize Typer app and Rich console
app = typer.Typer()
console = Console()

def connect_to_database():
    """Establish a connection to the SQLite database.This function is responsible for establishing a connection to the SQLite database.
    It does not take any arguments and does not return any value. Upon successful
    connection, it prints a confirmation message to the console."""

    console.print("Connected to the database", style="bold green")

@app.command("start")
def start():
    """Start the Library CLI.
    This function is the entry point for the Library CLI application."""

    console.print("Welcome to Library CLI!\n", style="bold green")
    connect_to_database()
    typer.secho("You can execute the command '--help' to see the possible commands")

@app.command("sign_up")
def sign_up(user_name: str, password: str):
    """Sign up a new user.
    This function is responsible for signing up a new user."""

    # Check if username already exists
    cursor.execute("SELECT * FROM user WHERE user_name = ?", (user_name,))
    existing_user = cursor.fetchone()
    if existing_user:
        typer.echo("Error: Username already in use. Please choose another username.")
        return

    # Add user to the database
    cursor.execute("INSERT INTO user (user_name, password) VALUES (?, ?)", (user_name, password))
    conn.commit()
    typer.echo(f"User {user_name} signed up successfully!")

@app.command("delete_user")
def delete_user(user_name: str):
    """Delete a user from the database.
    This function is responsible for deleting a user from the database."""

    # Check if user exists
    cursor.execute("SELECT user_id FROM user WHERE user_name = ?", (user_name,))
    user_id = cursor.fetchone()
    if not user_id:
        typer.echo("Error: User not found.")
        return

    user_id = user_id[0]

    # Delete associated records from related tables
    cursor.execute("DELETE FROM borrowed_books WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM read_books WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM favorite_books WHERE user_id = ?", (user_id,))

    # Delete user
    cursor.execute("DELETE FROM user WHERE user_id = ?", (user_id,))
    conn.commit()

    typer.echo(f"User '{user_name}' deleted successfully.")


@app.command("sign_in")
def sign_in(user_name: str, password: str):
    """Sign in a user.
    This function is responsible for signing in a user by verifying the provided
    username and password against the database"""

    cursor.execute("SELECT * FROM user WHERE user_name = ? AND password = ?", (user_name, password))
    user = cursor.fetchone()
    if user:
        typer.echo(f"Welcome back, {user_name}!")
    else:
        typer.echo("Error: Invalid username or password.")

@app.command("search_by_name")
def search_by_name(book_name: str):
    """Search for books by name.
    This function allows users to search for books by their name."""

    cursor.execute("SELECT * FROM book WHERE name LIKE ?", (f'%{book_name}%',))
    books = cursor.fetchall()
    if books:
        for book in books:
            console.print(f"Book ID: {book[0]}, Name: {book[1]}, Author: {book[2]}", style="bold blue")
    else:
        typer.echo("No books found with that name.")

@app.command("search_by_author")
def search_by_author(author: str):
    """Search for books by author.
    This function allows users to search for books by their author."""

    cursor.execute("SELECT * FROM book WHERE author LIKE ?", (f'%{author}%',))
    books = cursor.fetchall()
    if books:
        for book in books:
            console.print(f"Book ID: {book[0]}, Name: {book[1]}, Author: {book[2]}", style="bold blue")
    else:
        typer.echo("No books found by that author.", style="bold red")


@app.command("most_read_books")
def most_read_books(genre: Optional[str] = None):
    """Display the 10 most-read books.
    This function retrieves and displays the 10 most-read books from the database."""

    if genre:
        cursor.execute("""
            SELECT book.book_id, book.name, book.author, COUNT(read_books.read_id) AS read_count
            FROM book
            LEFT JOIN read_books ON book.book_id = read_books.book_id
            WHERE book.genre = ?
            GROUP BY book.book_id
            ORDER BY read_count DESC
            LIMIT 10
        """, (genre,))
    else:
        cursor.execute("""
            SELECT book.book_id, book.name, book.author, COUNT(read_books.read_id) AS read_count
            FROM book
            LEFT JOIN read_books ON book.book_id = read_books.book_id
            GROUP BY book.book_id
            ORDER BY read_count DESC
            LIMIT 10
        """)
    books = cursor.fetchall()

    if books:
        console.print("\nMost Read Books:\n", style="bold blue")
        for book in books:
            console.print(f"Book ID: {book[0]}, Name: {book[1]}, Author: {book[2]}, Read Count: {book[3]}", style="bold green")
    else:
        typer.echo("No read books found.")


@app.command("recently_added")
def recently_added(genre: Optional[str] = None):
    """Display the 5 most recent books added.
    This function retrieves and displays the 5 most recent books added to the database."""

    if genre:
        cursor.execute("SELECT * FROM book WHERE genre = ? ORDER BY date_added DESC LIMIT 5", (genre,))
    else:
        cursor.execute("SELECT * FROM book ORDER BY date_added DESC LIMIT 5")
    books = cursor.fetchall()
    
    if books:
        console.print("\nRecent Books:\n", style="bold blue")
        for book in books:
            console.print(f"Book ID: {book[0]}, Name: {book[1]}, Author: {book[2]}, Added By: {book[4]}", style="bold green")
    else:
        typer.echo("No recent books found.")

@app.command("most_read_genres")
def most_read_genres():
    """Display the 5 most-read genres.
     This function retrieves and displays the 5 most-read genres from the database."""
    
    cursor.execute("""
        SELECT book.genre, COUNT(read_books.read_id) AS read_count
        FROM book
        LEFT JOIN read_books ON book.book_id = read_books.book_id
        GROUP BY book.genre
        ORDER BY read_count DESC
        LIMIT 5
    """)
    genres = cursor.fetchall()

    if genres:
        console.print("\nMost Read Genres:\n", style="bold blue")
        for genre in genres:
            console.print(f"Genre: {genre[0]}, Read Count: {genre[1]}", style="bold green")
    else:
        typer.echo("No read genres found.")


@app.command("most_read_authors")
def most_read_authors():
    """Display the 3 most-read authors.
    This function retrieves and displays the 3 most-read authors from the database."""

    cursor.execute("""
        SELECT book.author, COUNT(read_books.read_id) AS read_count
        FROM book
        LEFT JOIN read_books ON book.book_id = read_books.book_id
        GROUP BY book.author
        ORDER BY read_count DESC
        LIMIT 3
    """)
    authors = cursor.fetchall()

    if authors:
        console.print("\nMost Read Authors:\n", style="bold blue")
        for author in authors:
            console.print(f"Author: {author[0]}, Read Count: {author[1]}", style="bold green")
    else:
        typer.echo("No read authors found.")


@app.command("add_book")
def add_book(username: str):
    """Add a book to the database.
    This function allows users to add a new book to the database. """

    name = typer.prompt("Enter the name of the book:")
    author = typer.prompt("Enter the author of the book:")
    pages = typer.prompt("Enter the number of pages:", type=int)
    genre = typer.prompt("Enter the genre of the book:")

    # Get user ID based on username
    user_id = get_user_id(username)

    # Check if the book already exists
    cursor.execute("SELECT * FROM book WHERE name = ? AND author = ?", (name, author))
    existing_book = cursor.fetchone()

    if existing_book:
        # Increment the quantity of the existing book
        cursor.execute("UPDATE book SET quantity = quantity + 1 WHERE book_id = ?", (existing_book[0],))
        conn.commit()
        typer.echo(f"Book '{name}' by {author} already exists. Quantity incremented.")
    else:
        # Add the new book to the database
        cursor.execute("""
            INSERT INTO book (name, author, pages, genre, quantity, date_added, added_by) 
            VALUES (?, ?, ?, ?, 1, ?, ?)
        """, (name, author, pages, genre, datetime.today(), user_id))
        conn.commit()
        typer.echo("Book added successfully.")


@app.command("delete_book")
def delete_book(book_id: int):
    """Delete a book from the database.
     This function allows users to delete a book from the database using its ID."""
    
    # Check if book exists
    cursor.execute("SELECT * FROM book WHERE book_id = ?", (book_id,))
    existing_book = cursor.fetchone()
    if not existing_book:
        typer.echo("Error: Book not found.")
        return

    # Delete associated records from related tables
    cursor.execute("DELETE FROM borrowed_books WHERE book_id = ?", (book_id,))
    cursor.execute("DELETE FROM read_books WHERE book_id = ?", (book_id,))
    cursor.execute("DELETE FROM favorite_books WHERE book_id = ?", (book_id,))

    # Delete book
    cursor.execute("DELETE FROM book WHERE book_id = ?", (book_id,))
    conn.commit()

    typer.echo(f"Book with ID {book_id} deleted successfully.")


@app.command("borrow_book")
def borrow_book(book_id: int, username: str):
    """This function allows a signed-in user to borrow a book from the library by specifying
    the book ID and their username."""
    
    # Check if the user is authenticated (signed in)
    if not is_authenticated(username):
        typer.echo("Error: You need to sign in before borrowing a book.")
        return

    # Check if the book is available
    cursor.execute("SELECT quantity FROM book WHERE book_id = ?", (book_id,))
    quantity = cursor.fetchone()
    if quantity is None or quantity[0] == 0:
        typer.echo("Error: This book is not available for borrowing.")
        return

    # Update database to reflect book borrowing
    borrow_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO borrowed_books (user_id, book_id, borrow_date) VALUES (?, ?, ?)",
                   (get_user_id(username), book_id, borrow_date))
    cursor.execute("UPDATE book SET quantity = quantity - 1 WHERE book_id = ?", (book_id,))
    conn.commit()

    typer.echo("Book borrowed successfully.")


def is_authenticated(username: str) -> bool:
    """Check if the user is authenticated.
     This function checks if the user is authenticated (signed in) by querying the
    database for the provided username."""

    cursor.execute("SELECT * FROM user WHERE user_name = ?", (username,))
    user = cursor.fetchone()
    return user is not None

def get_user_id(username: str) -> int:
    """Retrieve the user ID based on the username from the database."""
    cursor.execute("SELECT user_id FROM user WHERE user_name = ?", (username,))
    user = cursor.fetchone()
    if user:
        return user[0]  # Return the user_id if the user exists
    else:
        return None  # Return None if the user does not exist


@app.command("return_book")
def return_book(book_id: int, username: str):
    """This command allows a user to return a borrowed book to the library."""

    # Check if the user is authenticated (signed in)
    if not is_authenticated(username):
        typer.echo("Error: You need to sign in before returning a book.")
        return

    # Check if the book is borrowed by the user
    cursor.execute("SELECT * FROM borrowed_books WHERE book_id = ? AND user_id = (SELECT user_id FROM user WHERE user_name = ?)", (book_id, username))
    borrowed_book = cursor.fetchone()

    # If the book is not borrowed by the user, check if it's borrowed by any user (including null user_id)
    if borrowed_book is None:
        cursor.execute("SELECT * FROM borrowed_books WHERE book_id = ? AND user_id IS NULL", (book_id,))
        borrowed_book = cursor.fetchone()
        if borrowed_book is None:
            typer.echo("Error: You have not borrowed this book.")
            return

    # Update database to reflect book return
    if borrowed_book[1] is None:  # If user_id is null
        cursor.execute("DELETE FROM borrowed_books WHERE borrow_id = ?", (borrowed_book[0],))
    else:
        cursor.execute("DELETE FROM borrowed_books WHERE book_id = ? AND user_id = ?", (book_id, borrowed_book[1]))

    cursor.execute("UPDATE book SET quantity = quantity + 1 WHERE book_id = ?", (book_id,))
    conn.commit()

    typer.echo("Book returned successfully.")


@app.command("mark_read")
def mark_read(book_id: int, username: str):
    """This command allows a signed-in user to mark a book as read."""
    # Check if the user is authenticated (signed in)
    if not is_authenticated(username):
        typer.echo("Error: You need to sign in before marking a book as read.")
        return

    # Update database to mark the book as read for the user
    read_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO read_books (user_id, book_id, read_date) VALUES (?, ?, ?)",
                   (get_user_id(username), book_id, read_date))
    conn.commit()

    typer.echo("Book marked as read successfully.")



@app.command("fav_book")
def fav_book(book_id: int, username: str):
    """This command allows a signed-in user to add a book to their favorites list."""

    # Check if the user is authenticated (signed in)
    if not is_authenticated(username):
        typer.echo("Error: You need to sign in before adding a book to favorites.")
        return

    # Update database to add the book to favorites for the user
    favorite_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO favorite_books (user_id, book_id, favorite_date) VALUES (?, ?, ?)",
                   (get_user_id(username), book_id, favorite_date))
    conn.commit()

    typer.echo("Book added to favorites successfully.")


@app.command("my_books")
def my_books(username: str):
    """This command allows a signed-in user to view their books."""

    # Check if the user is authenticated (signed in)
    if not is_authenticated(username):
        typer.echo("Error: You need to sign in to view your books.")
        return

    # Query database to retrieve books read and favorited by the user
    cursor.execute("""
        SELECT b.book_id, b.name, b.author, 'Read' AS status
        FROM book b
        JOIN read_books r ON b.book_id = r.book_id
        WHERE r.user_id = (SELECT user_id FROM user WHERE user_name = ?)
        UNION
        SELECT b.book_id, b.name, b.author, 'Favorite' AS status
        FROM book b
        JOIN favorite_books f ON b.book_id = f.book_id
        WHERE f.user_id = (SELECT user_id FROM user WHERE user_name = ?)
    """, (username, username))
    user_books = cursor.fetchall()

    # Display user's books
    if user_books:
        typer.echo("Your Books:")
        for book in user_books:
            typer.echo(f"Book ID: {book[0]}, Name: {book[1]}, Author: {book[2]}, Status: {book[3]}")
    else:
        typer.echo("You haven't read or favorited any books yet.")


@app.command("statistics")
def statistics(username: str):
    """ This command retrieves reading statistics for the signed-in user
    from the database and displays them."""
    # Check if the user is authenticated (signed in)
    if not is_authenticated(username):
        typer.echo("Error: You need to sign in to view your statistics.")
        return

    # Query database to retrieve statistics
    cursor.execute("""
        SELECT COUNT(DISTINCT rb.book_id) AS num_books_read,
               COUNT(DISTINCT b.author) AS num_authors_read,
               COUNT(DISTINCT b.genre) AS num_genres_read,
               SUM(b.pages) AS total_pages_read
        FROM read_books rb
        JOIN book b ON rb.book_id = b.book_id
        WHERE rb.user_id = (SELECT user_id FROM user WHERE user_name = ?)
    """, (username,))
    statistics = cursor.fetchone()

    # Display statistics
    typer.echo("Your Reading Statistics:")
    typer.echo(f"Number of Books Read: {statistics[0]}")
    typer.echo(f"Number of Authors Read: {statistics[1]}")
    typer.echo(f"Number of Genres Read: {statistics[2]}")
    typer.echo(f"Total Pages Read: {statistics[3]}")

if __name__ == "__main__":
    app()

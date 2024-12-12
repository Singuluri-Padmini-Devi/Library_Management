import express from 'express';
import { PythonShell } from 'python-shell';
import sqlite3 from 'sqlite3';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import dotenv from 'dotenv';

const __dirname = dirname(fileURLToPath(import.meta.url));
dotenv.config();

const app = express();
app.use(express.json());

// Initialize SQLite database
const db = new sqlite3.Database(join(__dirname, 'library.db'));

// Create tables
db.serialize(() => {
  db.run(`CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE,
    hashed_password TEXT,
    is_librarian BOOLEAN DEFAULT FALSE
  )`);

  db.run(`CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    author TEXT,
    isbn TEXT UNIQUE,
    copies INTEGER
  )`);

  db.run(`CREATE TABLE IF NOT EXISTS borrow_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    book_id INTEGER,
    start_date TEXT,
    end_date TEXT,
    status TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(book_id) REFERENCES books(id)
  )`);
});

// Routes
app.post('/api/auth/login', (req, res) => {
  const { email, password } = req.body;
  db.get('SELECT * FROM users WHERE email = ?', [email], (err, user) => {
    if (err) {
      res.status(500).json({ error: 'Database error' });
      return;
    }
    if (!user) {
      res.status(401).json({ error: 'Invalid credentials' });
      return;
    }
    // In production, use proper password hashing
    if (password === user.hashed_password) {
      res.json({ token: 'dummy-token', user_id: user.id });
    } else {
      res.status(401).json({ error: 'Invalid credentials' });
    }
  });
});

app.get('/api/books', (req, res) => {
  db.all('SELECT * FROM books', (err, books) => {
    if (err) {
      res.status(500).json({ error: 'Database error' });
      return;
    }
    res.json(books);
  });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
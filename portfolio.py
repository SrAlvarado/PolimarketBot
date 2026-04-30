import sqlite3
import os

DB_FILE = "cartera.db"

def get_connection():
    return sqlite3.connect(DB_FILE)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Tabla de la cuenta
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS account (
            id INTEGER PRIMARY KEY,
            balance REAL NOT NULL
        )
    """)
    
    # Insertar balance inicial si no existe
    cursor.execute("SELECT COUNT(*) FROM account")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO account (id, balance) VALUES (1, 1000.0)")
        
    # Tabla de posiciones
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS positions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            market_id TEXT NOT NULL,
            market_title TEXT NOT NULL,
            decision TEXT NOT NULL,
            invested_usd REAL NOT NULL,
            shares REAL NOT NULL,
            status TEXT DEFAULT 'OPEN',
            pnl REAL DEFAULT 0.0,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

def get_balance():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM account WHERE id = 1")
    balance = cursor.fetchone()[0]
    conn.close()
    return balance

def update_balance(amount_change):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE account SET balance = balance + ? WHERE id = 1", (amount_change,))
    conn.commit()
    conn.close()

def record_trade(market_id, market_title, decision, invested_usd, shares):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO positions (market_id, market_title, decision, invested_usd, shares)
        VALUES (?, ?, ?, ?, ?)
    """, (market_id, market_title, decision, invested_usd, shares))
    conn.commit()
    conn.close()

def get_open_positions():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, market_id, market_title, decision, invested_usd, shares FROM positions WHERE status = 'OPEN'")
    positions = cursor.fetchall()
    conn.close()
    
    return [
        {
            "id": p[0],
            "market_id": p[1],
            "market_title": p[2],
            "decision": p[3],
            "invested_usd": p[4],
            "shares": p[5]
        }
        for p in positions
    ]

def close_position(position_id, won):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT invested_usd, shares FROM positions WHERE id = ?", (position_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return 0
        
    invested_usd, shares = row
    
    if won:
        pnl = shares - invested_usd # Ganancia neta (cada share vale 1 usd si gana)
        payout = shares
    else:
        pnl = -invested_usd # Pierde lo invertido
        payout = 0
        
    cursor.execute("UPDATE positions SET status = 'CLOSED', pnl = ? WHERE id = ?", (pnl, position_id))
    conn.commit()
    conn.close()
    
    return payout, pnl

def get_total_pnl():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(pnl) FROM positions WHERE status = 'CLOSED'")
    total = cursor.fetchone()[0]
    conn.close()
    return total if total else 0.0

if __name__ == "__main__":
    init_db()
    print(f"Base de datos inicializada. Balance actual: ${get_balance():.2f}")

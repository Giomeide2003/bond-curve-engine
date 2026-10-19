import sqlite3
from pathlib import Path


dossier_projet = Path(__file__).resolve().parent
fichier_base = dossier_projet / "bond_curve.db"

with sqlite3.connect(fichier_base) as connexion:
    connexion.execute("""
        CREATE TABLE IF NOT EXISTS market_ticks (
            tick_id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            asset_symbol TEXT NOT NULL,
            asset_class TEXT NOT NULL,
            event_time TEXT NOT NULL,
            event_type TEXT NOT NULL
                CHECK (event_type IN ('quote', 'trade')),
            bid_price REAL,
            ask_price REAL,
            trade_price REAL,
            volume REAL,
            source_event_id TEXT,

            CHECK (
                event_type != 'quote'
                OR (bid_price IS NOT NULL AND ask_price IS NOT NULL)
            ),
            CHECK (
                event_type != 'trade'
                OR trade_price IS NOT NULL
            ),
            CHECK (
                bid_price IS NULL
                OR ask_price IS NULL
                OR bid_price <= ask_price
            ),
            UNIQUE (source, asset_symbol, source_event_id)
        )
    """)

    connexion.execute("""
        CREATE INDEX IF NOT EXISTS idx_market_ticks_asset_time
        ON market_ticks (asset_symbol, event_time)
    """)

print("Table market_ticks créée dans :", fichier_base)
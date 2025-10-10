from sqlalchemy import create_engine, text
from config.settings import DB_URL
import pandas as pd

engine = create_engine(DB_URL, echo=False)

def execute_query(query: str) -> pd.DataFrame:
    with engine.connect() as conn:
        result = conn.execute(text(query))
        rows = result.fetchall()
        cols = result.keys()
        return pd.DataFrame(rows, columns=cols)

import sqlite3
import pandas as pd
from datetime import datetime
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "suivi_citernes.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Table Citernes
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS citernes (
        code TEXT PRIMARY KEY,
        type TEXT NOT NULL, -- 'CARBURANT' or 'EAU'
        comments TEXT DEFAULT '',
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    # Table Etapes
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS etapes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        citerne_type TEXT NOT NULL,
        category TEXT NOT NULL,
        step_name TEXT NOT NULL,
        cadence_hours REAL DEFAULT 1.0,
        step_order INTEGER NOT NULL
    );
    """)
    
    # Table Suivi Progress
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS suivi_progress (
        citerne_code TEXT NOT NULL,
        step_id INTEGER NOT NULL,
        completion_pct REAL DEFAULT 0.0,
        comment TEXT DEFAULT '',
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (citerne_code, step_id),
        FOREIGN KEY (citerne_code) REFERENCES citernes (code) ON DELETE CASCADE,
        FOREIGN KEY (step_id) REFERENCES etapes (id) ON DELETE CASCADE
    );
    """)
    
    # Table Daily Snapshots for historical tracking
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS daily_snapshots (
        snapshot_date TEXT NOT NULL,
        citerne_code TEXT NOT NULL,
        step_id INTEGER NOT NULL,
        completion_pct REAL DEFAULT 0.0,
        PRIMARY KEY (snapshot_date, citerne_code, step_id)
    );
    """)
    
    conn.commit()
    conn.close()

def get_all_citernes(citerne_type=None):
    conn = get_connection()
    if citerne_type:
        df = pd.read_sql_query("SELECT * FROM citernes WHERE type = ? ORDER BY code", conn, params=(citerne_type,))
    else:
        df = pd.read_sql_query("SELECT * FROM citernes ORDER BY type, code", conn)
    conn.close()
    return df

def get_etapes(citerne_type):
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM etapes WHERE citerne_type = ? ORDER BY step_order", conn, params=(citerne_type,))
    conn.close()
    return df

def get_citerne_details(citerne_code):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM citernes WHERE code = ?", (citerne_code,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_citerne_progress(citerne_code):
    conn = get_connection()
    query = """
    SELECT 
        e.id as step_id,
        e.category,
        e.step_name,
        e.cadence_hours,
        e.step_order,
        COALESCE(p.completion_pct, 0.0) as completion_pct,
        COALESCE(p.comment, '') as step_comment,
        p.updated_at
    FROM etapes e
    JOIN citernes c ON c.type = e.citerne_type
    LEFT JOIN suivi_progress p ON p.citerne_code = c.code AND p.step_id = e.id
    WHERE c.code = ?
    ORDER BY e.step_order
    """
    df = pd.read_sql_query(query, conn, params=(citerne_code,))
    conn.close()
    return df

def update_step_progress(citerne_code, step_id, completion_pct, comment=None):
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if comment is not None:
        cursor.execute("""
        INSERT INTO suivi_progress (citerne_code, step_id, completion_pct, comment, updated_at)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(citerne_code, step_id) DO UPDATE SET
            completion_pct = excluded.completion_pct,
            comment = excluded.comment,
            updated_at = excluded.updated_at
        """, (citerne_code, step_id, float(completion_pct), str(comment), now))
    else:
        cursor.execute("""
        INSERT INTO suivi_progress (citerne_code, step_id, completion_pct, comment, updated_at)
        VALUES (?, ?, ?, '', ?)
        ON CONFLICT(citerne_code, step_id) DO UPDATE SET
            completion_pct = excluded.completion_pct,
            updated_at = excluded.updated_at
        """, (citerne_code, step_id, float(completion_pct), now))
        
    cursor.execute("UPDATE citernes SET updated_at = ? WHERE code = ?", (now, citerne_code))
    conn.commit()
    conn.close()

def update_citerne_comment(citerne_code, comment):
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("UPDATE citernes SET comments = ?, updated_at = ? WHERE code = ?", (str(comment), now, citerne_code))
    conn.commit()
    conn.close()

def get_summary_dataframe(citerne_type=None):
    conn = get_connection()
    
    query_c = "SELECT code, type, comments, updated_at FROM citernes"
    if citerne_type:
        query_c += f" WHERE type = '{citerne_type}'"
    query_c += " ORDER BY type, code"
    
    citernes_df = pd.read_sql_query(query_c, conn)
    
    # Get total cadence per type
    cadence_df = pd.read_sql_query("SELECT citerne_type, SUM(cadence_hours) as total_cadence FROM etapes GROUP BY citerne_type", conn)
    cadence_dict = dict(zip(cadence_df['citerne_type'], cadence_df['total_cadence']))
    
    # Calculate progress for each citerne
    query_p = """
    SELECT 
        c.code,
        c.type,
        SUM((COALESCE(p.completion_pct, 0.0) / 100.0) * e.cadence_hours) as completed_hours,
        COUNT(CASE WHEN COALESCE(p.completion_pct, 0.0) >= 100 THEN 1 END) as steps_done,
        COUNT(e.id) as total_steps
    FROM citernes c
    JOIN etapes e ON e.citerne_type = c.type
    LEFT JOIN suivi_progress p ON p.citerne_code = c.code AND p.step_id = e.id
    """
    if citerne_type:
        query_p += f" WHERE c.type = '{citerne_type}'"
    query_p += " GROUP BY c.code, c.type"
    
    prog_df = pd.read_sql_query(query_p, conn)
    conn.close()
    
    merged = pd.merge(citernes_df, prog_df, on=['code', 'type'], how='left')
    merged['total_cadence'] = merged['type'].map(cadence_dict)
    merged['global_pct'] = (merged['completed_hours'] / merged['total_cadence'] * 100.0).round(1)
    merged['global_pct'] = merged['global_pct'].fillna(0.0)
    
    def get_status(row):
        pct = row['global_pct']
        if pct >= 99.9:
            return "Terminé"
        elif pct > 0:
            return "En cours"
        else:
            return "Non commencé"
            
    merged['statut'] = merged.apply(get_status, axis=1)
    return merged

def get_category_progress_df(citerne_type):
    conn = get_connection()
    query = """
    SELECT 
        e.category,
        AVG(COALESCE(p.completion_pct, 0.0)) as avg_completion,
        SUM((COALESCE(p.completion_pct, 0.0)/100.0) * e.cadence_hours) / SUM(e.cadence_hours) * 100.0 as weighted_completion
    FROM etapes e
    JOIN citernes c ON c.type = e.citerne_type
    LEFT JOIN suivi_progress p ON p.citerne_code = c.code AND p.step_id = e.id
    WHERE e.citerne_type = ?
    GROUP BY e.category
    ORDER BY MIN(e.step_order)
    """
    df = pd.read_sql_query(query, conn, params=(citerne_type,))
    conn.close()
    df['weighted_completion'] = df['weighted_completion'].round(1)
    df['avg_completion'] = df['avg_completion'].round(1)
    return df

def export_full_matrix(citerne_type):
    conn = get_connection()
    
    etapes = get_etapes(citerne_type)
    citernes = get_all_citernes(citerne_type)
    
    query = """
    SELECT 
        c.code as Citerne,
        e.step_order,
        e.step_name,
        COALESCE(p.completion_pct, 0.0) as completion
    FROM citernes c
    JOIN etapes e ON e.citerne_type = c.type
    LEFT JOIN suivi_progress p ON p.citerne_code = c.code AND p.step_id = e.id
    WHERE c.type = ?
    """
    p_df = pd.read_sql_query(query, conn, params=(citerne_type,))
    conn.close()
    
    pivot = p_df.pivot(index='Citerne', columns='step_name', values='completion')
    
    # Order columns by step_order
    step_order_names = etapes['step_name'].tolist()
    pivot = pivot.reindex(columns=step_order_names)
    
    summary = get_summary_dataframe(citerne_type).set_index('code')
    
    matrix = summary[['type', 'statut', 'global_pct', 'comments', 'updated_at']].copy()
    matrix.columns = ['Type', 'Statut', 'Avancement Global (%)', 'Commentaires', 'Dernière Maj']
    
    final_df = pd.concat([matrix, pivot], axis=1)
    return final_df

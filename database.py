import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
import pandas as pd

class TaskDatabase:
    def __init__(self, db_name: str = "tasks.db"):
        self.db_name = db_name
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Projects table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                goal TEXT NOT NULL,
                deadline TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'active'
            )
        ''')
        
        # Tasks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                task_name TEXT NOT NULL,
                description TEXT,
                estimated_duration TEXT,
                start_date TEXT,
                end_date TEXT,
                dependencies TEXT,
                priority TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_project(self, goal: str, deadline: str) -> int:
        """Save a new project and return its ID"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute(
            'INSERT INTO projects (goal, deadline) VALUES (?, ?)',
            (goal, deadline)
        )
        
        project_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return project_id
    
    def save_tasks(self, project_id: int, tasks: List[Dict]):
        """Save multiple tasks for a project"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        for task in tasks:
            cursor.execute('''
                INSERT INTO tasks 
                (project_id, task_name, description, estimated_duration, 
                start_date, end_date, dependencies, priority, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                project_id,
                task['name'],
                task.get('description', ''),
                task.get('duration', ''),
                task.get('start_date', ''),
                task.get('end_date', ''),
                json.dumps(task.get('dependencies', [])),
                task.get('priority', 'medium'),
                'pending'
            ))
        
        conn.commit()
        conn.close()
    
    def get_all_projects(self) -> pd.DataFrame:
        """Retrieve all projects"""
        conn = sqlite3.connect(self.db_name)
        df = pd.read_sql_query('SELECT * FROM projects ORDER BY created_at DESC', conn)
        conn.close()
        return df
    
    def get_project_tasks(self, project_id: int) -> pd.DataFrame:
        """Retrieve all tasks for a specific project"""
        conn = sqlite3.connect(self.db_name)
        df = pd.read_sql_query(
            'SELECT * FROM tasks WHERE project_id = ? ORDER BY id',
            conn,
            params=(project_id,)
        )
        conn.close()
        return df
    
    def update_task_status(self, task_id: int, status: str):
        """Update task status"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute(
            'UPDATE tasks SET status = ? WHERE id = ?',
            (status, task_id)
        )
        
        conn.commit()
        conn.close()
    
    def delete_project(self, project_id: int):
        """Delete a project and all its tasks"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM tasks WHERE project_id = ?', (project_id,))
        cursor.execute('DELETE FROM projects WHERE id = ?', (project_id,))
        
        conn.commit()
        conn.close()

from fastapi import FastAPI, HTTPException
import psycopg2
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db_connection():
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    return conn


class Student(BaseModel):
    id: int = None
    name: str = None
    course: str = None



#Get all students
@app.get('/students')
def get_all_students():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT * FROM students')
        rows = cursor.fetchall()
        result = []
        for row in rows:
            result.append({
                'id': row[0],
                'name': row[1],
                'course': row[2]
            })
        return result
    finally:
        cursor.close()
        conn.close()

#get single student
@app.get('/students/{id}')
def get_single_student(id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT * FROM students WHERE id=%s', (id,))
        row = cursor.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail='Student Record Not FOUND')
        return {
            'id': row[0],
            'name': row[1],
            'course': row[2]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=404, detail='Student Record Not FOUND')
    finally:
        cursor.close()
        conn.close()

#create student record
@app.post('/students')
def create_student_record(student: Student):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO students VALUES (%s, %s, %s)', (student.id, student.name, student.course))
        conn.commit()
        return {
            'message': 'Student record created successfully'
        }
    except psycopg2.IntegrityError:
        conn.rollback()
        raise HTTPException(status_code=404, detail="Student Record Already Exists")
    finally:
        cursor.close()
        conn.close()


# Replace Student Record
@app.put("/students/{id}")
def replace_student_record(id: int, student: Student):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE students SET id=%s, name=%s, course=%s WHERE id=%s",
            (student.id, student.name, student.course, id)
        )
        if cursor.rowcount == 0:
            conn.rollback()
            raise HTTPException(
                status_code=404,
                detail="Student ID not found"
            )
        conn.commit()
        return {
            "message": "Student record updated successfully"
        }
    except HTTPException:
        raise
    except psycopg2.IntegrityError:
        conn.rollback()
        raise HTTPException(
            status_code=409,
            detail="The new student ID already exists"
        )
    finally:
        cursor.close()
        conn.close()


#Replace one Column
@app.patch('/students/{id}')
def partially_update_student_record(id: int, student: Student):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if student.id is not None:
            cursor.execute('UPDATE students SET id=%s WHERE id=%s', (student.id, id))
            conn.commit()
        if student.name is not None:
            cursor.execute('UPDATE students SET name=%s WHERE id=%s', (student.name, id))
            conn.commit()
        if student.course is not None:
            cursor.execute('UPDATE students SET course=%s WHERE id=%s', (student.course, id))
            conn.commit()
        return {
            'message': 'Student record updated successfully'
        }
    finally:
        cursor.close()
        conn.close()

@app.delete('/students/{id}')
def delete_student_record(id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM students WHERE id=%s', (id,))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail='Student ID not found')
        else:
            return {
                'message': 'Student record deleted successfully'
            }
    finally:
        cursor.close()
        conn.close()

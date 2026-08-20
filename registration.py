"""
registration.py
Manages the Registrations junction table (student_id + course_id).
Uses dropdowns (Combobox) populated from Students and Courses instead
of typed-in IDs, since guessing IDs is error-prone.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from mysql.connector import Error
from database import db
from student import StudentManager
from course import CourseManager


# ---------- CRUD manager ----------
class RegistrationManager:
    def register_student(self, student_id, course_id):
        try:
            cursor = db.get_cursor()
            # Uses the stored procedure created in schema.sql
            cursor.callproc('RegisterStudent', [student_id, course_id])
            db.connection.commit()
            cursor.close()
            return True
        except Error as e:
            raise Exception(f"Could not register student: {e}")

    def get_registered_courses(self, student_id):
        cursor = db.get_cursor()
        query = """SELECT r.registration_id, c.course_code, c.course_name
                   FROM Registrations r
                   JOIN Courses c ON r.course_id = c.course_id
                   WHERE r.student_id = %s"""
        cursor.execute(query, (student_id,))
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def unregister(self, registration_id):
        try:
            cursor = db.get_cursor()
            cursor.execute("DELETE FROM Registrations WHERE registration_id=%s", (registration_id,))
            db.connection.commit()
            cursor.close()
            return cursor.rowcount > 0
        except Error as e:
            raise Exception(f"Could not remove registration: {e}")


# ---------- GUI frame ----------
class RegistrationFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.manager = RegistrationManager()
        self.student_manager = StudentManager()
        self.course_manager = CourseManager()

        # id -> label maps, built when dropdowns are refreshed
        self.student_map = {}
        self.course_map = {}
        self.registration_id_map = {}

        self._build_form()
        self._build_table()
        self.refresh_dropdowns()

    def _build_form(self):
        form = tk.LabelFrame(self, text="Register a Student for a Course", padx=10, pady=10)
        form.pack(fill="x", padx=10, pady=10)

        tk.Label(form, text="Student").grid(row=0, column=0, sticky="w")
        self.student_combo = ttk.Combobox(form, state="readonly", width=40)
        self.student_combo.grid(row=0, column=1, padx=5, pady=2)
        self.student_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_table())

        tk.Label(form, text="Course").grid(row=1, column=0, sticky="w")
        self.course_combo = ttk.Combobox(form, state="readonly", width=40)
        self.course_combo.grid(row=1, column=1, padx=5, pady=2)

        btn_frame = tk.Frame(form)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)
        tk.Button(btn_frame, text="Register", command=self.register).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Refresh Lists", command=self.refresh_dropdowns).pack(side="left", padx=5)

    def _build_table(self):
        tk.Label(self, text="Courses registered by selected student:").pack(anchor="w", padx=10)
        columns = ("reg_id", "code", "name")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        self.tree.heading("reg_id", text="Registration ID")
        self.tree.heading("code", text="Course Code")
        self.tree.heading("name", text="Course Name")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        tk.Button(self, text="Unregister Selected", command=self.unregister).pack(pady=5)

    def refresh_dropdowns(self):
        try:
            students = self.student_manager.get_all_students()
            self.student_map = {
                f"{s['first_name']} {s['last_name']} (ID {s['student_id']})": s["student_id"]
                for s in students
            }
            self.student_combo["values"] = list(self.student_map.keys())

            courses = self.course_manager.get_all_courses()
            self.course_map = {
                f"{c['course_code']} - {c['course_name']}": c["course_id"]
                for c in courses
            }
            self.course_combo["values"] = list(self.course_map.keys())
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        self.registration_id_map = {}
        student_label = self.student_combo.get()
        if not student_label:
            return
        student_id = self.student_map.get(student_label)
        try:
            regs = self.manager.get_registered_courses(student_id)
            for r in regs:
                item = self.tree.insert("", "end", values=(r["registration_id"], r["course_code"], r["course_name"]))
                self.registration_id_map[item] = r["registration_id"]
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def register(self):
        student_label = self.student_combo.get()
        course_label = self.course_combo.get()
        if not student_label or not course_label:
            messagebox.showwarning("Missing selection", "Choose both a student and a course.")
            return
        try:
            self.manager.register_student(
                self.student_map[student_label],
                self.course_map[course_label]
            )
            messagebox.showinfo("Success", "Student registered for course.")
            self.refresh_table()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def unregister(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("No selection", "Select a registration row first.")
            return
        if not messagebox.askyesno("Confirm", "Remove this registration?"):
            return
        try:
            self.manager.unregister(self.registration_id_map[selected])
            self.refresh_table()
        except Exception as e:
            messagebox.showerror("Error", str(e))
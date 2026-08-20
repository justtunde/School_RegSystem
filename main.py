"""
main.py
Entry point. Opens one window with a tab per module.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from database import db
from student import StudentFrame
from department import DepartmentFrame
from lecturer import LecturerFrame
from course import CourseFrame
from registration import RegistrationFrame
from reports import ReportsFrame
# Build this one last, once you're comfortable with the pattern:



class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Student Course Registration System")
        self.geometry("900x650")

        try:
            db.connect()
        except Exception as e:
            messagebox.showerror("Connection Error",
                                  f"Could not connect to MySQL:\n{e}")

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        notebook.add(StudentFrame(notebook), text="Students")
        notebook.add(DepartmentFrame(notebook), text="Departments")
        notebook.add(LecturerFrame(notebook), text="Lecturers")
        notebook.add(CourseFrame(notebook), text="Courses")
        notebook.add(RegistrationFrame(notebook), text="Registration")
        notebook.add(ReportsFrame(notebook), text="Reports")


if __name__ == "__main__":
    app = App()
    app.mainloop()
# from flask import Flask
# import pymysql

# app = Flask(__name__)

# conn = pymysql.connect(
#     host='localhost',
#     user='root',
#     password='bhushanbhatta',
#     db='mydb',
#     port=3306,
#     autocommit=True  # so changes commit automatically
# )

# @app.route('/')
# def test_mysql():
#     try:
#         with conn.cursor() as cur:
#             # Create table if not exists
#             cur.execute("""
#                 CREATE TABLE IF NOT EXISTS students (
#                     id INT AUTO_INCREMENT PRIMARY KEY,
#                     name VARCHAR(100),
#                     age INT
#                 );
#             """)

#             # Insert sample data
#             cur.execute("INSERT INTO students (name, age) VALUES (%s, %s);", ("Alice", 21))
#             cur.execute("INSERT INTO students (name, age) VALUES (%s, %s);", ("Bob", 22))

#             # Fetch data
#             cur.execute("SELECT * FROM students;")
#             rows = cur.fetchall()

#             # Format output
#             result = "Students:<br>"
#             for row in rows:
#                 result += f"ID: {row[0]}, Name: {row[1]}, Age: {row[2]}<br>"

#             return result

#     except Exception as e:
#         return f"❌ Error: {str(e)}"

# if __name__ == '__main__':
#     app.run(debug=True)

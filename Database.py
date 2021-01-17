import sqlite3

connection = sqlite3.connect("myDatabase.db")
#https://repl.it/talk/learn/How-to-create-an-SQLite3-database-in-Python-3/15755
#Example:
# with Database() as db:
#	 result = db("SELECT * FROM emp")
#	 result = result.fetchall()
class Database(object):
	def __enter__(self):
		self.conn = sqlite3.connect("myDatabase.db")
		return self
	def __exit__(self, exc_type, exc_val, exc_tb):
		self.conn.close()

	def __call__(self, query):
		c = self.conn.cursor()
		try:
			result = c.execute(query)
			self.conn.commit()
		except Exception as e:
			result = e
		return result
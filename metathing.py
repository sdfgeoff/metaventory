import sqlite3
import sys
import argparse


def ensure_db_integrity(db):
	cursor = db.cursor()
	cursor.execute(
		'CREATE TABLE if not exists "things"'
		'('
			'"id" INTEGER PRIMARY KEY AUTOINCREMENT,'
			'"name" TEXT'
		')'
	)
	cursor.execute(
		'CREATE TABLE if not exists "owners"'
		'('
			'"owner_id" INTEGER,'
			'"thing_id" INTEGER,'
			'"quantity" INTEGER,'
			'PRIMARY KEY("owner_id", "thing_id"),'
			'FOREIGN KEY ("owner_id") REFERENCES "things"("id")'
			'FOREIGN KEY ("thing_id") REFERENCES "things"("id")'
		')'
	)
	db.commit()


def create_thing(db, thing):
	cursor = db.cursor()
	cursor.execute('INSERT INTO "things" (name) VALUES (?)', [thing])
	db.commit()
	return cursor.lastrowid


def get_name(db, thing_id):
	cursor = db.cursor()
	cursor.execute('SELECT (name) FROM "things" WHERE (id) = (?)', [thing_id])
	db.commit()
	thing = cursor.fetchone()
	if thing:
		return thing[0]
	return None


def delete_thing(db, thing_id):
	"""Removes a thing from the database. Returns True if succesful, False
	if the item doesn't exists, and None if removal failed due to existing
	ownership relations"""
	cursor = db.cursor()
	try:
		cursor.execute('DELETE FROM "things" WHERE (id) = (?)', [thing_id])
	except sqlite3.IntegrityError:
		return None

	db.commit()
	if cursor.rowcount == 1:
		return True
	return False


def set_quantity_owned(db, owner_id, thing_id, quantity):
	"""
	Sets how many instance of one thing another thing ownes. Note
	that zero is a valid quantity and is used for things like categories
	etc. Presence in the owners table is what indicates ownership
	so to stop an object being owned, you have to use the 
	remove_ownership function.
	"""
	cursor = db.cursor()
	cursor.execute('INSERT OR IGNORE INTO "owners" (owner_id, thing_id, quantity) VALUES (?,?,0);', (owner_id, thing_id))
	cursor.execute('UPDATE "owners" SET quantity=? WHERE (owner_id, thing_id) = (?,?)', (quantity, owner_id, thing_id))
	db.commit()


def get_quantity_owned(db, owner_id, thing_id):
	"""Returns the quantity owned (which can be zero) or None of there
	is no ownership"""
	cursor = db.cursor()
	cursor.execute('SELECT (quantity) FROM "owners" WHERE (owner_id, thing_id) = (?, ?)', (owner_id, thing_id))
	db.commit()
	thing = cursor.fetchone()
	if thing:
		return thing[0]
	return None


def remove_ownership(db, owner_id, thing_id):
	"""Removes a thing from the database. Returns True if succesful"""
	cursor = db.cursor()
	cursor.execute('DELETE FROM "owners" WHERE (owner_id, thing_id) = (?, ?)', [owner_id, thing_id])
	
	db.commit()
	if cursor.rowcount == 1:
		return True
	return None


def main(args):
	db = sqlite3.connect('test.db')
	ensure_db_integrity(db)

	
if __name__ == "__main__":
	main(sys.argv)

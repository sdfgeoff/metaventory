import metathing
import sqlite3
import sys

def gen_db():
	db = sqlite3.connect(':memory:')
	db.execute("PRAGMA foreign_keys = 1")
	
	# Ensure databse is empty
	cursor = db.cursor()
	cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
	db.commit()
	assert cursor.fetchone() == None, "message"
	
	metathing.ensure_db_integrity(db)
	return db

def test_create_get_delete_thing():
	db = gen_db()
	thing_id = metathing.create_thing(db, "thing7")
	assert metathing.get_name(db, thing_id) == "thing7"
	assert metathing.delete_thing(db, thing_id) == True
	assert metathing.get_name(db, thing_id) == None


def test_get_nonexistant_thing():
	db = gen_db()
	assert metathing.get_name(db, -5) == None


def test_delete_nonexistant_thing():
	db = gen_db()
	assert metathing.delete_thing(db, -5) == False


def test_create_same_name_thing():
	db = gen_db()
	thing1_id = metathing.create_thing(db, "thing7")
	thing2_id = metathing.create_thing(db, "thing7")
	assert thing1_id != thing2_id


def test_set_get_owned_quantity():
	"""Tests that you can set and get the owned quantity"""
	db = gen_db()
	thing_id = metathing.create_thing(db, "thing7")
	owner_id = metathing.create_thing(db, "thing8")
	
	metathing.set_quantity_owned(db, owner_id, thing_id, 5)
	assert metathing.get_quantity_owned(db, owner_id, thing_id) == 5
	
	metathing.set_quantity_owned(db, owner_id, thing_id, 8)
	assert metathing.get_quantity_owned(db, owner_id, thing_id) == 8


def test_remove_ownership_removes_ownership():
	db = gen_db()
	thing_id = metathing.create_thing(db, "thing7")
	owner_id = metathing.create_thing(db, "thing8")
	
	metathing.set_quantity_owned(db, owner_id, thing_id, 5)
	assert metathing.get_quantity_owned(db, owner_id, thing_id) == 5
	
	metathing.remove_ownership(db, owner_id, thing_id)
	assert metathing.get_quantity_owned(db, owner_id, thing_id) == None


def test_unowned_quantity_is_none():
	""" If an object is not owned by another, it should return None.
	Note that ownership can occur with zero quantity. See assoated
	test_owned_zero_quantity_ios_zero"""
	db = gen_db()
	thing1_id = metathing.create_thing(db, "thing7")
	thing2_id = metathing.create_thing(db, "thing8")
	assert metathing.get_quantity_owned(db, thing1_id, thing2_id) == None
	assert metathing.get_quantity_owned(db, thing2_id, thing1_id) == None


def test_owned_zero_quantity_is_zero():
	"""Ensure that zero quantity does not remove ownership link"""
	db = gen_db()
	owner_id = metathing.create_thing(db, "thing7")
	thing_id = metathing.create_thing(db, "thing8")
	metathing.set_quantity_owned(db, owner_id, thing_id, 0)
	assert metathing.get_quantity_owned(db, owner_id, thing_id) == 0


def test_delete_with_ownership_reference_fails():
	db = gen_db()
	owner_id = metathing.create_thing(db, "thing7")
	thing_id = metathing.create_thing(db, "thing8")
	metathing.set_quantity_owned(db, owner_id, thing_id, 1)
	assert metathing.delete_thing(db, owner_id) == None

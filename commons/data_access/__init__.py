import tim_commons.db


def add(row):
  tim_commons.db.Session().add(row)
  flush()


def delete(row):
  tim_commons.db.Session().delete(row)
  flush()


def flush():
  tim_commons.db.Session().flush()

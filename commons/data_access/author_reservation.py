import data_access
import tim_commons.db
import mi_schema.models


add_author_reservation = data_access.add


def delete_author_reservation(author_name):
  query = tim_commons.db.Session().query(mi_schema.models.AuthorReservation)
  query = query.filter_by(author_name=author_name)
  query.delete()

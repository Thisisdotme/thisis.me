class DummyMessageClient:
  def basic_publish(self, exchange=None, routing_key=None, body=None):
    return object()

  def wait(self, promise):
    pass

  def close(self):
    pass

  def queue_declare(self, queue=None, durable=None):
    pass


class DummyDBSession:
  class _Query:
    def filter(self, something):
      return self

    def first(self):
      return None

    def filter_by(self, **kargs):
      return self

    def count(self):
      return 10

    def __getitem__(self, key):
      return self

  def query(self, clazz):
    return DummyDBSession._Query()

  def add(self, table_object):
    pass

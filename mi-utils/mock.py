class DummyMessageClient:
  def basic_publish(self, *args, **kargs):
    return object()

  def wait(self, promise):
    pass

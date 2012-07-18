import sys
import datetime
import threading

from tim_commons import app_base, message_queue, db
from event_scanner import scan_events


class ScannerApplication(app_base.AppBase):
  def app_main(self, config, options, args):
    db_url = db.create_url_from_config(config['db'])
    message_url = message_queue.create_url_from_config(config['broker'])

    maximum_priority = int(config['scanner']['maximum_priority'])
    iteration_minimum_duration = float(config['scanner']['iteration_minimum_duration'])
    iteration_minimum_duration = datetime.timedelta(seconds=iteration_minimum_duration)

    db.configure_session(db_url)

    message_client = message_queue.create_message_client(message_url)
    message_queue.create_queues_from_config(message_client, config['queues'])
    message_queue.close_message_client(message_client)

    scanners = []
    for priority in range(0, maximum_priority + 1):
      scanner = threading.Thread(target=scan_events,
                                 args=(message_url,
                                       priority,
                                       iteration_minimum_duration,
                                       maximum_priority))
      scanner.start()
      scanners.append(scanner)

    for scanner in scanners:
      scanner.join()


if __name__ == '__main__':
  sys.exit(ScannerApplication('event_scanner', daemon_able=True).main())

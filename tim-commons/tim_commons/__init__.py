def total_seconds(td):
  return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10 ** 6) / 10 ** 6


def prune_dictionary(source_dict, prune_dict):
  for prune_key, prune_value in prune_dict.iteritems():
    if not prune_key in source_dict:
      continue
    if prune_value:
      prune_dictionary(source_dict[prune_key], prune_value)
    else:
      del source_dict[prune_key]

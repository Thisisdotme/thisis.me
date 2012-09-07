def to_JSON_dictionary(feature, request):
  return {'id': feature.id,
          'name': feature.name,
          'images': {
            'color': {
              'high_res': None,
              'med_res': None,
              'low_res': None
            },
            'mono': {
              'high_res': None,
              'med_res': None,
              'low_res': None
            }
          },
          'text': {
            'label': None,
            'description': None
          }
         }

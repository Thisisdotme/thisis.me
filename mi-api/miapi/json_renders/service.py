'''
Created on Aug 13, 2012

@author: howard
'''


def to_JSON_dictionary(service, request):
  return {'id': service.id,
          'name': service.service_name,
          'images': {
            'color': {
              'high_res': request.static_url('miapi:%s' % service.color_icon_high_res),
              'med_res': request.static_url('miapi:%s' % service.color_icon_medium_res),
              'low_res': request.static_url('miapi:%s' % service.color_icon_low_res)
            },
            'mono': {
              'high_res': request.static_url('miapi:%s' % service.mono_icon_high_res),
              'med_res': request.static_url('miapi:%s' % service.mono_icon_medium_res),
              'low_res': request.static_url('miapi:%s' % service.mono_icon_low_res)
            }
          },
          'text': {
            'label': None,
            'description': None
          }
         }

"""
    print structure of edx course

"""


from argparse import ArgumentParser
from sys import exit as process_terminate
from traceback import format_exc

from opaque_keys.edx.keys import CourseKey
from openedx.core.djangoapps.content.course_structures.api.v0.api import course_structure


if __name__ == "__main__":
	try:
		# Parsing arguments
		parser = ArgumentParser(description=r'A Simple tool of Mysql tables tables checking.')
		parser.add_argument('--key', required=True, default='', help='course key string')
        args = parser.parse_args()

        outline = course_structure(CourseKey.from_string(args.cert_folder))
        outline = outline['blocks']
        my_outline = {}
        for block_id, block in outline.iteritems():
            if block['type'] == "chapter":
                children = {}
                for child in block['children']:
                    children[child] = {'pretty': "", "children": {}}
                my_outline[block_id] = {
                    'pretty': "%s < %s > - %s" % (block_id, block['type'], block['display_name']),
                    'children': children
                }
        for block_id, block in outline.iteritems():
            if block['type'] == "sequential":
                children = {}
                for child in block['children']:
                    children[child] = {'pretty': "", "children": {}}
                for chapter_id, chapter in my_outline.iteritems():
                    if block_id in chapter['children'].keys():
                        chapter['children'][block_id]['pretty'] = "%s < %s > - %s" % (
                        block_id, block['type'], block['display_name'])
                        chapter['children'][block_id]['children'] = children
        for block_id, block in outline.iteritems():
            if block['type'] == "vertical":
                children = {}
                for child in block['children']:
                    children[child] = {'pretty': "", "children": {}}
                for chapter_id, chapter in my_outline.iteritems():
                    for sequential_id, sequential in chapter['children'].iteritems():
                        if block_id in sequential['children'].keys():
                            sequential['children'][block_id]['pretty'] = "%s < %s > - %s" % (
                            block_id, block['type'], block['display_name'])
                            sequential['children'][block_id]['children'] = children
        for block_id, block in outline.iteritems():
            if block['type'] not in ["chapter", "sequential", "vertical"]:
                children = {}
                for chapter_id, chapter in my_outline.iteritems():
                    for sequential_id, sequential in chapter['children'].iteritems():
                        for vertical_id, vertical in sequential['children'].iteritems():
                            if block_id in vertical['children'].keys():
                                vertical['children'][block_id]['pretty'] = "%s < %s > - %s" % (
                                block_id, block['type'], block['display_name'])
        for chapter_id, chapter in my_outline.iteritems():
            print
            chapter['pretty'].encode('utf-8')
            for sequential_id, sequential in chapter['children'].iteritems():
                print
                "    |____ %s" % sequential['pretty'].encode('utf-8')
                for vertical_id, vertical in sequential['children'].iteritems():
                    print
                    "        |____ %s" % vertical['pretty'].encode('utf-8')
                    for block_id, block in vertical['children'].iteritems():
                        print
                        "            |____ %s" % block['pretty'].encode('utf-8')

            print(r'[DONE]')

	except Exception:
		print(r'[Exception]: {err_msg}'.format(err_msg=format_exc()))
		process_terminate(12)

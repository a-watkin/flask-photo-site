import os
import sys

try:
    # Running as flask app.
    from common.database_interface import Database
except Exception as e:
    # Running as module.
    sys.path.append(os.getcwd())
    from common.database_interface import Database


class Tag(object):

    def __init__(self):
        self.db = Database()
        self.username = 'a'

    def get_tag(self, tag_name):
        return self.db.get_query_as_list(
            '''
            select tag_name from tag where tag_name = "{}"
            '''.format(tag_name)
        )

    def add_tag(self, tag_name):
        query_string = '''
        insert into tag (tag_name, username)
        values (?,?)
        '''

        data = (
            tag_name,
            self.username
        )

        self.db.make_sanitized_query(query_string, data)

        if self.get_tag(tag_name):
            return True
        return False

    def delete_tag(self, tag_name):
        resp = self.db.make_query(
            '''
            delete from tag where tag_name = "{}"
            '''.format(tag_name)
        )

        if not resp:
            return True
        return False

    def update_tag(self, tag_name):
        query_string = '''
        update tag 
        set tag_name = ?
        '''

        data = (
            tag_name,
        )

        if self.db.make_sanitized_query(query_string, data):
            return True
        return False

    def get_all_tag_names(self):
        """
        Get all tag names as a list.
        """
        tag_data = self.db.get_query_as_list(
            '''
            SELECT tag_name FROM tag ORDER BY tag_name
            '''
        )

        tags = []

        for tag in tag_data:
            tags.append(list(tag.values())[0])

        return tags

    def check_for_blank_tags(self):
        """
        Check for and remove blank tags.
        """
        tags = self.get_all_tag_names()
        for tag in tags:
            if tag == '':
                print('blank tag', tag)
                self.delete_tag(tag)


if __name__ == "__main__":
    t = Tag()
    print(t.check_for_blank_tags())

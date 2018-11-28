from database_interface import Database
import sqlite3


class Tag(object):

    def __init__(self):
        self.db = Database('eigi-data.db')

    def get_all_tags(self):
        tag_data = self.db.get_query_as_list("SELECT tag_name FROM tag")

        rtn_dict = {

        }

        count = 0
        for t in tag_data:
            rtn_dict[count] = t
            count += 1

        return rtn_dict

    def get_photo_tags(self, photo_id):
        """
        Get the tags for a single photo.
        """

        query_string = '''
            select photo.photo_id, photo.photo_title, photo_tag.tag_name from photo
            join photo_tag on(photo_tag.photo_id=photo.photo_id)
            where photo.photo_id={}
        '''.format(photo_id)

        tag_data = self.db.get_query_as_list(query_string)
        print(tag_data)

    def get_photos_by_tag(self, tag_name):
        """
        Get all the photos that are associated with a particular tag.

        I will need to handle spaces.
        """
        q_data = None

        query_string = '''
            select photo_id, photo_title, views, tag_name, original from photo 
            join photo_tag using(photo_id)
            join images using(photo_id)
            where tag_name={}
            order by views desc
        '''.format("'" + tag_name + "'")

        data = self.db.get_query_as_list(query_string)

        print(data)
        # with sqlite3.connect(self.db.db_name) as connection:
        #     c = connection.cursor()
        #     q_data = c.execute(query_string)

        #     # print(row)

        # print(q_data)

        # tag_data = self.db.get_query_as_list(query_string)
        # print(tag_data)


if __name__ == "__main__":
    t = Tag()
    # print(t.get_all_tags())
    print(t.get_photos_by_tag('london'))
    # print(t.get_photo_tags(5052580779))

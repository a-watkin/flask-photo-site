from database_interface import Database
import sqlite3


class Tag(object):

    def __init__(self):
        self.db = Database('eigi-data.db')

    def get_all_tags(self):
        tag_data = self.db.get_query_as_list("SELECT tag_name FROM tag")

        # print(tag_data)

        rtn_dict = {
            # 'tag_info': {'number_of_photos': self.get_photo_count_by_tag(tag_name)}
        }

        count = 0
        for t in tag_data:
            rtn_dict[count] = t
            tag_name = t['tag_name']
            # adding the number of photos with the tag
            rtn_dict[count]['photos'] = self.get_photo_count_by_tag(
                t['tag_name'])
            count += 1

        return rtn_dict

    def get_photo_tags(self, photo_id):
        """
        Get the tags for a single photo.

            select photo.photo_id, photo.photo_title, photo_tag.tag_name from photo
            join photo_tag on(photo_tag.photo_id=photo.photo_id)
            where photo.photo_id={}

        """

        query_string = '''
            select photo_tag.tag_name from photo
            join photo_tag on(photo_tag.photo_id=photo.photo_id)
            where photo.photo_id={}
        '''.format(photo_id)

        # so an array of tags would be ok
        tag_data = self.db.get_query_as_list(query_string)
        # print(tag_data)

        return tag_data

    def get_photo_count_by_tag(self, tag_name):
        query_string = '''select count(photo_id) from photo
        join photo_tag using(photo_id)
        where tag_name = '{}'  '''.format(tag_name)

        photo_count = self.db.get_query_as_list(query_string)

        if len(photo_count) > 0:
            return photo_count[0]['count(photo_id)']

    def get_photos_by_tag(self, tag_name):
        """
        Get all the photos that are associated with a particular tag.

        I will need to handle spaces.
        """
        q_data = None

        query_string = '''
            select photo_id, photo_title, views, tag_name, large_square from photo 
            join photo_tag using(photo_id)
            join images using(photo_id)
            where tag_name={}
            order by views desc
        '''.format("'" + tag_name + "'")

        tag_data = self.db.get_query_as_list(query_string)

        rtn_dict = {
            'tag_info': {'number_of_photos': self.get_photo_count_by_tag(tag_name)}
        }

        count = 0
        for t in tag_data:
            rtn_dict[count] = t
            count += 1

        return rtn_dict

    def update_tag(self, new_name, tag_name):
        update_string = '''
                        update photo_tag
                        set tag_name = '{}'
                        where tag_name = '{}' 
                        '''.format(new_name, tag_name)

        # print(update_string)

        # Check if new tag name already exists
        tag_data = self.db.get_rows('tag')
        all_tags = [x[0] for x in tag_data]

        if new_name in all_tags:
            print('TAG ALREADY EXISTS')
            """
            get the data relating to the old tag name and save it

            Get data from photo_tag

            Get data from tag

            Save the above

            Delete both from the database

            Reenter the data with the corrected tag
            """
            #

        # print(all_tags.values())

        # for t in all_tags:
        #     print('\n', all_tags[t])

        # if new_name in all_tags:
        #     return True

        # photo_count = self.db.get_query_as_list(query_string)


if __name__ == "__main__":
    t = Tag()
    # print(t.get_all_tags())

    # This is actually a special case as the new_name is for an existing tag
    print(t.update_tag('people', 'peope'))

    # print(t.get_photos_by_tag('apples'))
    # print(t.get_photo_tags(5052580779))

    # print(t.get_photo_count_by_tag('apples'))

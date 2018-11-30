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

    def update_tag(self, new_tag, old_tag):
        # Check if the tag is already in the database
        check = self.db.make_query(
            '''
            select tag_name from tag where tag_name = '{}'
            '''.format(new_tag)
        )

        # Save the data to be updated from photo_data
        photo_tag_query = '''
                        select * from photo_tag
                        where tag_name = '{}' 
                        '''.format(old_tag)

        # get the old tags photo_tag data
        photo_tag_data = self.db.make_query(photo_tag_query)

        # prepare data for insert back, change the values that you need to change
        new_photo_tag_data = []
        # update photo_tag and delete the old tag name from tag
        for v in photo_tag_data:
            new_photo_tag_data.append((v[0], new_tag))

        # if the new tag is not in the table tag then add it
        if len(check) == 0:
            print('tag is not in the table tag, so adding it')
            self.db.insert_data({
                'table': 'tag',
                'tag_name': new_tag,
                'user_id': '28035310@N00'
            })

        # otherwise the new_tag is in the tag table and doesn't need to be added

        # insert new tag into photo_tag
        self.db.insert_tag_data('photo_tag', new_photo_tag_data)

        # it doesn't cascade on delete so delete the old tag
        self.db.delete_rows_where('tag', 'tag_name', old_tag)

        # delete the old tag from photo_tag
        self.db.delete_rows_where('photo_tag', 'tag_name', old_tag)


if __name__ == "__main__":
    t = Tag()
    # print(t.get_all_tags())

    # This is actually a special case as the new_name is for an existing tag
    print(t.update_tag('people', 'peope'))

    # print(t.get_photos_by_tag('apples'))
    # print(t.get_photo_tags(5052580779))

    # print(t.get_photo_count_by_tag('apples'))

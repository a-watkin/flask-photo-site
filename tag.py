import urllib.parse
import sqlite3


from common.database_interface import Database
from common import name_util


class Tag(object):

    def __init__(self):
        self.db = Database('eigi-data.db')

    # get count of photos using tag
    def get_photo_count_by_tag(self, tag_name):
        if '%' in tag_name:
            tag_name = urllib.parse.quote(tag_name, safe='')

        query_string = '''
            SELECT count(photo_id) FROM photo
            JOIN photo_tag USING(photo_id)
            WHERE tag_name = "{}"
        '''.format(tag_name)

        photo_count = self.db.get_query_as_list(query_string)

        return photo_count[0]['count(photo_id)']

    def remove_tag_name(self, tag_name):
        tag_name = name_util.make_encoded(tag_name)

        self.db.make_query(
            '''
            DELETE FROM tag WHERE tag_name = "{}"
            '''.format(tag_name)
        )

        self.db.make_query(
            '''
            DELETE FROM photo_tag WHERE tag_name = "{}"
            '''.format(tag_name)
        )

    def delete_tag(self, tag_name):
        """
        Deletes the specified tag from the database.
        """
        # Remove tag from tag table.
        self.db.delete_rows_where('tag', 'tag_name', tag_name)
        # Remove photo from photo_tag.
        self.db.delete_rows_where('photo_tag', 'tag_name', tag_name)

        if not self.get_tag(tag_name) and not self.check_photo_tag(tag_name):
            return True
        else:
            return False

    def update_photo_count(self, tag_name):
        """
        Updates the photo count for the given tag.
        """
        count = self.get_photo_count_by_tag(tag_name)

        if count > 0:
            self.db.make_query(
                '''
                UPDATE tag
                SET photos = {}
                WHERE tag_name = "{}"
                '''.format(count, tag_name)
            )
        else:
            self.delete_tag(tag_name)

    def check_all_tag_photo_counts(self):
        """
        Gets a count of all the photos associated with a tag.
        Checks that the photos column in tag is up to date.
        """
        data = self.db.get_query_as_list(
            '''
            SELECT * FROM tag
            '''
        )

        for tag in data:
            # query for the number of photos using the tag
            # compare it to the number in the photos column
            # update if necessary
            query_count = self.db.get_query_as_list(
                '''
                SELECT count(tag_name)
                FROM photo_tag
                WHERE tag_name = "{}"
                '''.format(tag['tag_name'])
            )

            if query_count[0]['count(tag_name)'] == tag['photos']:
                print('OK', 'actual photos number with tag',
                      query_count[0]['count(tag_name)'], 'in photos column', tag['photos'])
            else:
                print('MISSMATCH IN PHOTOS AND PHOTOS WITH TAG\n', 'actual photos number with tag',
                      query_count[0]['count(tag_name)'], 'in photos column', tag['photos'])

                tag_name = tag['tag_name']
                count = query_count[0]['count(tag_name)']
                break

        print('\nDONE NO PROBLEMS!')

    def remove_zero_photo_tags(self):
        self.check_all_tag_photo_counts()

        zero_photos = self.db.make_query(
            '''
            DELETE FROM tag WHERE photos = 0
            '''
        )

    def get_zero_photo_tag_count(self):
        return self.db.make_query(
            '''
            SELECT COUNT(photos) FROM tag WHERE photos = 0
            '''
        )[0][0]

    def get_all_tags(self):
        # Tags as a list of dict values.
        tag_data = self.db.get_query_as_list(
            "SELECT tag_name, photos FROM tag ORDER BY tag_name"
        )

        rtn_dict = {

        }

        count = 0
        for tag in tag_data:
            rtn_dict[count] = tag
            tag_name = tag['tag_name']
            # Adding the number of photos with the tag.
            rtn_dict[count]['photos'] = tag['photos']
            rtn_dict[count]['human_readable_tag'] = name_util.make_decoded(
                tag['tag_name'])
            count += 1

        return rtn_dict

    def get_photo_tags(self, photo_id):
        """
        Get the tags for a single photo.
        """
        query_string = '''
            SELECT photo_tag.tag_name FROM photo
            JOIN photo_tag ON(photo_tag.photo_id=photo.photo_id)
            WHERE photo.photo_id={}
        '''.format(photo_id)

        tag_data = self.db.get_query_as_list(query_string)
        for tag in tag_data:
            tag['human_readable_tag'] = name_util.make_decoded(tag['tag_name'])

        return tag_data

    def get_photos_by_tag(self, tag_name):
        """
        Get all the photos that are associated with a particular tag.
        """
        query_string = '''
            SELECT photo_id, photo_title, views, tag_name, large_square, date_taken FROM photo
            JOIN photo_tag USING(photo_id)
            JOIN images USING(photo_id)
            WHERE tag_name = "{}"
            ORDER BY date_taken DESC
        '''.format(tag_name)

        tag_data = self.db.get_query_as_list(query_string)

        rtn_dict = {
            'tag_info': {'number_of_photos': self.get_photo_count_by_tag(tag_name)}
        }

        count = 0
        for t in tag_data:
            rtn_dict[count] = t
            rtn_dict[count]['human_readable_tag'] = name_util.make_decoded(
                rtn_dict[count]['tag_name'])
            count += 1

        return rtn_dict

    def get_tag(self, tag_name):
        tag_data = self.db.make_query(
            '''
            SELECT tag_name FROM tag WHERE tag_name = "{}"
            '''.format(tag_name)
        )

        if len(tag_data) > 0:
            tag_name = tag_data[0][0]
            human_readable_tag = name_util.make_decoded(tag_data[0][0])

            rtn_dict = {
                'tag_name': tag_name,
                'human_readable_name': human_readable_tag
            }

            return rtn_dict

    def check_photo_tag(self, tag_name):
        """
        Checks that a tag has been added.

        Returns true if the tag is in photo_tag.

        Returns false if the tag is not in photo_tag.
        """
        data = self.db.make_query(
            '''SELECT * FROM photo_tag WHERE tag_name = "{}" '''
            .format(tag_name))

        # Remove any tags that have zero photos.
        self.get_photo_count_by_tag(tag_name)

        if len(data) > 0:
            return True
        return False

    # def clean_tags(self):
    #     forbidden = ['.', ';', '%']
    #     # Tags as a list of dict values.
    #     tag_data = self.db.get_query_as_list("SELECT * FROM tag")
    #     for tag in tag_data:
    #         if tag['tag_name'] in forbidden:
    #             self.remove_tag_name(tag['tag_name'])

    #     tag_data = self.db.get_query_as_list("SELECT * FROM photo_tag")
    #     for tag in tag_data:
    #         if tag['tag_name'] in forbidden:
    #             self.remove_tag_name(tag['tag_name'])

    def remove_tags_from_photo(self, photo_id, tag_list):
        """
        do you need to encode the tag list?
        """
        for tag in tag_list:
            print(tag)

            # if the tag isn't present it will just fail silently
            resp = self.db.make_query(
                '''
                DELETE FROM photo_tag
                WHERE photo_id = {}
                AND tag_name = "{}"
                '''.format(photo_id, tag)
            )
            print(resp)

            """
            check tag count here
            """
            if self.get_photo_count_by_tag(tag) <= 0:
                # remove the tag if it has no photos associated with it
                self.delete_tag(tag)
            else:
                # only update if you're not removing it
                self.update_photo_count(tag)

    def replace_tags(self, photo_id, tag_list):
        """
        Replaces the tags attached to a photo with new tags.
        """
        # get all the tags attached to the photo
        current_tags = self.db.make_query(
            '''
            SELECT * FROM photo_tag WHERE photo_id = {}
            '''.format(photo_id)
        )

        # remove the current tags
        self.db.make_query(
            '''
            DELETE FROM photo_tag WHERE photo_id = {}
            '''.format(photo_id)
        )

        for tag in tag_list:
            # add tags in the tag_list
            self.db.make_query(
                '''
                insert into photo_tag (photo_id, tag_name)
                values ({}, "{}")
                '''.format(photo_id, tag)
            )

            self.update_photo_count(tag)

    def add_tags_to_photo(self, photo_id, tag_list):
        """
        Adds tags to a photo.

        First checking if the tag is already in the tag table, if not it adds it.

        Then it adds the tag to photo_tag which links the photo and tag tables.
        """
        print('\nHello from add_tags_to_photo, the tag list is: ', tag_list)

        # for each tag
        # check if the tag is in the database already
        # if it is not then add it to the tag table
        for tag in tag_list:

            # will return None if the tag is not in the tag table
            # tag_name is the column name
            data = self.db.get_row('tag', 'tag_name', tag)

            print('data is', data)

            if data is None:

                print('\nthat value {} is not in the db\n'.format(tag))

                self.db.make_query(
                    '''
                    insert into tag (tag_name, user_id, photos)
                    values ("{}", "{}", {})
                    '''.format(
                        tag,
                        '28035310@N00',
                        self.get_photo_count_by_tag(tag)
                    )
                )

                print('\nshould be added now...\n')

                if self.db.get_row('tag', 'tag_name', tag):
                    print('\nadded tag, ', tag, '\n')

            # UNIQUE constraint can cause problems here
            # so catch any exceptions.
            try:
                # The tag is now in the database.
                self.db.make_query(
                    '''
                    insert into photo_tag (photo_id, tag_name)
                    values ({}, "{}")
                    '''.format(photo_id, tag)
                )
            except Exception as e:
                print('Problem adding tag to photo_tag ', e)

        data = self.db.make_query(
            '''
            SELECT * FROM photo_tag WHERE photo_id = {}
            '''.format(photo_id)
        )

        tags_in_data = []
        if len(data) > 0:
            for tag in data:
                tags_in_data.append(tag[1])

        for tag in tag_list:
            if tag not in tags_in_data:
                return False
            else:
                self.update_photo_count(tag)

        return True

    def update_tag(self, new_tag, old_tag):
        """
        Problem here when updating a tag to one that already exists
        """
        print('hello from update_tag - passed values, ', new_tag, old_tag)
        # check if new tag exists
        test = self.db.make_query(
            '''
            SELECT * FROM tag WHERE tag_name = "{}"
            '''.format(new_tag)
        )

        print(test)

        if not test:
            # if the tag doesn't exist already then update it
            # existing tag to the new tag
            self.db.make_query(
                '''
                update tag
                set tag_name = "{}"
                WHERE tag_name = "{}"
                '''.format(new_tag, old_tag)
            )

        try:
            # Tag exists.
            photos = self.get_photos_by_tag(old_tag)

            for photo in photos:
                print('photo data ', photo, photos)

                if photo:

                    # if new tag exists or not you have to update photo_tag
                    self.db.make_query(
                        '''
                        update photo_tag
                        set tag_name = "{}"
                        WHERE tag_name = "{}"
                        '''.format(new_tag, old_tag)
                    )

            self.delete_tag(old_tag)
        except Exception as e:
            print('problem updating tag name, ', e)
        finally:
            # tag already exists on photo
            self.delete_tag(old_tag)
            return True

        # update all photo_tag entries to the new tag

        # update the photo count for the tag table
        self.update_photo_count(new_tag)

        if self.get_tag(new_tag) and not self.get_tag(old_tag):
            return True
        else:
            return False

    def count_photos_by_tag_name(self, tag_name):
        count = self.db.make_query(
            '''
            SELECT count(tag_name)
            FROM photo_tag
            WHERE tag_name = "{}"
            '''.format(tag_name)
        )

        if len(count) > 0:
            return count[0][0]
        else:
            return 0

    def get_tag_photos_in_range(self, tag_name, limit=20, offset=0):
        # I think flask is passing decoded values in.
        tag_name = name_util.make_encoded(tag_name)

        # Get all photos associated with the tag name.
        num_photos = self.count_photos_by_tag_name(tag_name)

        if offset > num_photos:
            offset = num_photos - (num_photos % 20)

        page = offset // limit
        pages = num_photos // limit

        # Ensure the starting page is 1 instead of 0.
        if num_photos == 20:
            page = 1
            pages = 1

        elif num_photos > 20 and num_photos % 20 == 0:
            page += 1

        else:
            page += 1
            pages += 1

        # Guards against page being grater than the number of pages.
        if page > pages:
            # Prevents an empty set from being returned.
            offset = offset - 20
            page = pages

        q_data = None
        with sqlite3.connect(self.db.db_name) as connection:
            c = connection.cursor()

            c.row_factory = sqlite3.Row

            query_string = (
                '''
                SELECT photo_id, photo_title, views, date_taken, tag_name, large_square FROM photo
                JOIN photo_tag USING(photo_id)
                JOIN images USING(photo_id)
                WHERE tag_name = "{}"
                ORDER BY date_taken
                DESC LIMIT {} OFFSET {}
                '''
            ).format(tag_name, limit, offset)

            q_data = c.execute(query_string)

        rtn_dict = {
            'limit': limit,
            'offset': offset,
            'photos': []
        }

        data = [dict(ix) for ix in q_data]

        # Decode the title.
        for photo in data:
            if photo['photo_title'] is not None:
                photo['photo_title'] = name_util.make_decoded(
                    photo['photo_title'])

        a_dict = {}
        count = 0
        for d in data:
            a_dict[count] = d
            count += 1

        rtn_dict = {'photos': a_dict}

        rtn_dict['limit'] = limit
        rtn_dict['offset'] = offset
        rtn_dict['tag_name'] = tag_name
        rtn_dict['human_readable_name'] = name_util.make_decoded(tag_name)
        rtn_dict['page'] = page
        rtn_dict['pages'] = pages

        rtn_dict['tag_info'] = {
            'number_of_photos': self.get_photo_count_by_tag(tag_name)
        }

        return rtn_dict


if __name__ == "__main__":
    t = Tag()
    print(t.get_photo_count_by_tag('test'))
    print(t.get_photos_by_tag('lindon'))

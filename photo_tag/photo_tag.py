import string
import urllib.parse
import sqlite3


try:
    from common.database_interface import Database
    from common import name_util
    from tag.tag import Tag
except Exception as e:
    import os
    import sys
    sys.path.append(os.getcwd())
    from common.database_interface import Database
    from common import name_util
    from tag.tag import Tag


class PhotoTag(object):
    """
    This is really too complicated.

    Different parts of the system call it.

    It's all interdependent and terrible overall.
    """

    def __init__(self):
        self.db = Database()

    def check_tags(self):
        """
        Removes tags in the tag table that are not in the photo_tag table.
        """
        all_tags = self.db.get_query_as_list(
            '''
            SELECT tag_name FROM tag
            '''
        )

        all_tags = [x['tag_name'] for x in all_tags]
        all_photo_tags = self.get_all_photo_tags_as_list()

        tags_not_in_photo_tags = set(all_tags) - set(all_photo_tags)

        for tag in tags_not_in_photo_tags:
            self.remove_tag_name(tag)

    def count_photos_by_tag_name(self, tag_name):
        """
        Returns the number of photos associated with a tag.
        """
        return self.db.get_query_as_list(
            '''
            SELECT COUNT(photo_id) FROM photo_tag WHERE tag_name = "{}"
            '''.format(tag_name)
        )[0]['COUNT(photo_id)']

    def update_photo_count(self, tag_name=None):
        # Too many things call this method.
        print('being called', tag_name)
        """
        Updates the number of photos associated with tags in the tag table.
        """
        # This is fast enough and usually what is used.
        if tag_name is not None:
            tag_name = name_util.make_encoded(tag_name)
            self.db.make_query(
                '''
                UPDATE tag
                SET photos = {}
                WHERE tag_name = "{}"
                '''.format(self.count_photos_by_tag_name(tag_name), tag_name)
            )

        else:
            # This is slow.
            for tag in self.get_all_photo_tags_as_list():
                tag = name_util.make_encoded(tag_name)
                self.db.make_query(
                    '''
                    UPDATE tag
                    SET photos = {}
                    WHERE tag_name = "{}"
                    '''.format(self.count_photos_by_tag_name(tag), tag)
                )

    def get_all_photo_tags_as_list(self):
        """
        Returns a list of all the photo tags as a list of photo_tag values from the photo_tag table.
        """
        tag_data = self.db.get_query_as_list(
            '''
            SELECT tag_name FROM photo_tag ORDER BY tag_name ASC
            '''
        )

        tags = []
        for tag in tag_data:
            if tag['tag_name'] not in tags:
                tags.append(tag['tag_name'])

        return tags

    def get_photo_tag_list(self, photo_id):
        """
        Returns a list with tag values for the given photo as a list of photo_tag values from the photo_tag table.
        """
        tag_data = self.db.get_query_as_list(
            '''
            SELECT tag_name FROM photo_tag
            WHERE photo_id = {}
            ORDER BY tag_name ASC
            '''.format(photo_id)
        )

        tags = []
        if tag_data:
            for tag in tag_data:
                tags.append(list(tag.values())[0])

        return tags

    def add_photo_tag(self, photo_id, tag_name):
        """
        Associates a photo with a tag via the photo_tag table.

        tag_name is encoded before insertion in the db.
        """
        query_string = '''
            INSERT INTO photo_tag(photo_id, tag_name)
            VALUES(?,?)
            '''

        data = (
            photo_id,
            name_util.make_encoded(tag_name)
        )

        self.db.make_sanitized_query(
            query_string, data
        )

    def add_tags_to_photo(self, photo_id, tag_list):
        # I don't like this method.
        """
        photo_id is an int id representing a photo

        tag_list is a list of string values.


        Adds tags to a photo.

        First checking if the tag is already in the tag table, if not it adds it.

        Then it adds the tag to photo_tag which links the photo and tag tables.
        """
        # Keep track of which tags have been added.
        added_tags = []
        for tag in tag_list:
            if len(tag) > 0:
                # Remove starting and trailing whitespace.
                tag = tag.strip()
                # Encode tag to a safe version.
                tag = name_util.make_encoded(tag)

                # Check if tag is in the tag table.
                # Data will be None if the tag is not in the tag table.
                data = self.db.get_row('tag', 'tag_name', tag)

                if data is None:
                    # Add tag to the tag table.
                    self.db.make_query(
                        '''
                        insert into tag (tag_name, user_id, photos)
                        values ("{}", "{}", {})
                        '''.format(
                            tag,
                            '28035310@N00',
                            0
                        )
                    )

                # UNIQUE constraints can cause problems here
                # so catch any exceptions.
                try:
                    # Associate the tag with the specified photo.
                    self.db.make_query(
                        '''
                        INSERT INTO photo_tag (photo_id, tag_name)
                        VALUES ({}, "{}")
                        '''.format(photo_id, tag)
                    )

                except Exception as e:
                    print('Problem adding tag to photo_tag ', e)

        # Confirming the tags have been added.
        photo_tags = self.get_photo_tag_list(photo_id)
        for tag in added_tags:
            if tag not in photo_tags:
                return False
            else:
                self.update_photo_count(tag)

        self.check_tags()

        return True

    def remove_tag_name(self, tag_name):
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
        THIS DOES NOT SEEM TO WORK.

        Deletes the specified tag from the database.
        """
        # Remove photo from photo_tag.
        self.db.delete_rows_where('photo_tag', 'tag_name', tag_name)
        # Remove tag from tag table.
        self.db.delete_rows_where('tag', 'tag_name', tag_name)

        self.update_photo_count(tag_name)

        if not self.get_tag(tag_name) and not self.check_photo_tag(tag_name):
            return True
        else:
            return False

    def get_all_tags(self):
        """
        Returns all tag_name rows from photo_tags and orders them into a dict by the first letter of tag_name.

        Used by tags and edit tags endpoints.

        Returns a dict ordered by the first char of the tag_name also provides human readable tag names and photo counts
        """
        # Tags as a list of dict values.
        tag_data = self.db.get_query_as_list(
            "SELECT tag_name, photos FROM tag ORDER BY tag_name"
        )

        # Build the dict structure.
        rtn_dict = dict()
        keys = list(string.digits + string.ascii_uppercase)
        for x in keys:
            rtn_dict[x] = []

        # List of dict keys.
        test_keys = list(rtn_dict.keys())

        for tag in tag_data:
            tag['human_readable_tag'] = name_util.make_decoded(
                tag['tag_name'])
            # Test for and add starting letter to the correct dict key.
            if str(tag['tag_name'][0]).upper() in test_keys:
                rtn_dict[str(tag['tag_name'][0]).upper()].append(tag)
            else:
                # Catch any other values that don't fall into the keys.
                rtn_dict['Misc'].append(tag)

        return rtn_dict

    def get_photo_tags(self, photo_id):
        """
        Get the tags associated with a photo.

        Returns a list of dicts each dict has the tag_name and human_readable_tag.
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
        print('hello from get_photos_by_tag')
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
            'tag_info': {'number_of_photos': self.count_photos_by_tag_name(tag_name)}
        }

        count = 0
        for t in tag_data:
            rtn_dict[count] = t
            rtn_dict[count]['human_readable_tag'] = name_util.make_decoded(
                rtn_dict[count]['tag_name'])
            count += 1

        return rtn_dict

    def get_tag(self, tag_name):
        """
        Helper method.

        Accepts a tag_name string.

        Returns a dict with the tag_name and human readable version.
        """
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
        self.count_photos_by_tag_name(tag_name)

        if len(data) > 0:
            return True
        return False

    def remove_tags_from_photo(self, photo_id, tag_list):
        """
        do you need to encode the tag list?
        """
        for tag in tag_list:
            # If the tag isn't present it fails silently.
            resp = self.db.make_query(
                '''
                DELETE FROM photo_tag
                WHERE photo_id = {}
                AND tag_name = "{}"
                '''.format(photo_id, tag)
            )

            # check tag count here
            if self.get_photo_count_by_tag(tag) <= 0:
                # IS THIS ACTUALLY WORKING?
                # Remove the tag if it has no photos associated with it.
                self.delete_tag(tag)
            else:
                # Update the tag count.
                self.update_photo_count(tag)

    def replace_tags(self, photo_id, tag_list):
        # this is what i want for add tags
        """
        Replaces the tags associated with a specific photo with new tags.
        """
        # Get all the tags attached to the photo.
        current_tags = self.db.make_query(
            '''
            SELECT * FROM photo_tag WHERE photo_id = {}
            '''.format(photo_id)
        )

        # Remove the current tags.
        self.db.make_query(
            '''
            DELETE FROM photo_tag WHERE photo_id = {}
            '''.format(photo_id)
        )

        for tag in tag_list:
            # Add the tags in the tag_list.
            self.db.make_query(
                '''
                insert into photo_tag (photo_id, tag_name)
                values ({}, "{}")
                '''.format(photo_id, tag)
            )

            self.update_photo_count(tag)

    def update_tag(self, new_tag, old_tag):
        # THIS NEEDS TO BE SIMPLIFIED
        """
        Problem here when updating a tag to one that already exists
        """
        print('hello from update_tag - passed values, ', new_tag, old_tag)
        # Check if new tag is already in the tag table.
        test = self.db.make_query(
            '''
            SELECT * FROM tag WHERE tag_name = "{}"
            '''.format(new_tag)
        )

        if not test:
            # if the tag doesn't exist already then update it
            # existing tag to the new tag
            self.db.make_query(
                '''
                UPDATE tag
                SET tag_name = "{}"
                WHERE tag_name = "{}"
                '''.format(new_tag, old_tag)
            )

        try:
            # Tag exists.
            photos = self.get_photos_by_tag(old_tag)

            for photo in photos:
                # print('photo data ', photo, photos)

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

    def get_tag_photos_in_range(self, tag_name, limit=20, offset=0):
        # THIS ALSO SUCKS
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
            'number_of_photos': self.count_photos_by_tag_name(tag_name)
        }

        return rtn_dict


if __name__ == "__main__":
    pt = PhotoTag()
    # pt.add_photo_tag(3363788969, 'ass')
    # print(pt.get_tag('boots'))
    print(pt.get_photo_tags(3363788969))

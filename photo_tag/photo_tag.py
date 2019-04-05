import string
import urllib.parse
import sqlite3


try:
    from common.database_interface import Database
    from common import utils
    from tag.tag import Tag
except Exception as e:
    import os
    import sys
    sys.path.append(os.getcwd())
    from common.database_interface import Database
    from common import utils


class PhotoTag(object):
    def __init__(self):
        self.db = Database()
        self.user_id = '28035310@N00'

    def check_tags(self):
        """
        Removes tags in the tag table that are not in the photo_tag table.

        This is only a good idea if you're not using the tags table for other purposes.
        """
        all_tags = self.db.get_query_as_list(
            '''
            SELECT tag_name FROM tag
            '''
        )

        # All tags in the tags table as a list.
        all_tags = [x['tag_name'] for x in all_tags]
        all_photo_tags = self.get_all_photo_tags_as_list()
        # Set difference of the above two sets.
        # This should be empty if there are no problems with the counts.
        tags_not_in_photo_tags = set(all_tags) - set(all_photo_tags)
        # Remove any problem counts.
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

    def get_human_readable_photo_tag_list(self, photo_id):
        """
        Accepts a photo_id and returns the tags associated with the photo in a human readable form.

        Used to get data on the front end by add_tag in photo_tag_routes.
        """
        tags = self.get_photo_tag_list(photo_id)
        rtn_list = []
        for tag in tags:
            rtn_list.append(utils.make_decoded(tag))
        return rtn_list

    def update_photo_count(self, tag_name=None):
        """
        Updates the number of photos associated with tags in the tag table.

        Encodes tag before checking.
        """
        # This is fast enough and usually what is used.
        if tag_name is not None:
            tag_name = utils.make_encoded(tag_name)
            self.db.make_query(
                '''
                UPDATE tag
                SET photos = {}
                WHERE tag_name = "{}"
                '''.format(self.count_photos_by_tag_name(tag_name), tag_name)
            )

        else:
            # Check the entire tag table is no tag_name provided.
            # This is slow.
            for tag in self.get_all_photo_tags_as_list():
                tag = utils.make_encoded(tag)
                # Get the number of photos using the tag.
                count = self.count_photos_by_tag_name(tag)

                # Update the count.
                self.db.make_query(
                    '''
                    UPDATE tag
                    SET photos = {}
                    WHERE tag_name = "{}"
                    '''.format(count, tag)
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
            utils.make_encoded(tag_name)
        )

        self.db.make_sanitized_query(
            query_string, data
        )

    def add_tag(self, tag_name):
        """
        Adds a tag to the tag table.
        """
        query_string = '''
            INSERT INTO tag(tag_name, user_id, photos)
            VALUES(?,?,?)
            '''

        data = (
            tag_name, self.user_id, 0
        )

        self.db.make_sanitized_query(
            query_string, data
        )

    def add_tags_to_photo(self, photo_id, tag_list):
        """
        photo_id is an int id representing a photo

        tag_list is a list of string values.

        Adds tags to a photo.

        Used by React script upload_editor.js to add tags.

        Also used by add_tag.html template.

        First the tags on the photo are removed.
        Then the new tags are added.
        """

        # Remove old tags
        self.remove_tags_from_photo(photo_id)

        # Keep track of which tags have been added.
        added_tags = []
        for tag in tag_list:
            if len(tag) > 0:
                # Remove starting and trailing whitespace.
                tag = tag.strip()
                # Encode tag to a safe version.
                tag = utils.make_encoded(tag)

                # Check if tag is in the tag table.
                # Data will be None if the tag is not in the tag table.
                data = self.db.get_row('tag', 'tag_name', tag)
                if data is None:
                    # Add tag to the tag table.
                    self.add_tag(tag)

                self.add_photo_tag(photo_id, tag)
                added_tags.append(tag)

        # Confirming the tags have been added.
        photo_tags = self.get_photo_tag_list(photo_id)
        for tag in added_tags:
            self.update_photo_count(tag)
            if tag not in photo_tags:
                return False

        self.check_tags()

        return True

    def remove_tag_name(self, tag_name):
        """
        Removes the given tag from tag and photo_tag tables.
        """
        self.db.make_query(
            '''
            DELETE FROM photo_tag WHERE tag_name = "{}"
            '''.format(tag_name)
        )

        self.db.make_query(
            '''
            DELETE FROM tag WHERE tag_name = "{}"
            '''.format(tag_name)
        )

    def delete_tag(self, tag_name):
        """
        This works with unencoded values

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
            tag['human_readable_tag'] = utils.make_decoded(
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
            tag['human_readable_tag'] = utils.make_decoded(tag['tag_name'])

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
            'tag_info': {'number_of_photos': self.count_photos_by_tag_name(tag_name)}
        }

        count = 0
        for t in tag_data:
            rtn_dict[count] = t
            rtn_dict[count]['human_readable_tag'] = utils.make_decoded(
                rtn_dict[count]['tag_name'])
            count += 1

        return rtn_dict

    def get_tag(self, tag_name):
        """
        Helper method.

        Accepts a tag_name string.

        Returns a dict with the tag_name and human readable version from the tag table.
        """
        tag_data = self.db.make_query(
            '''
            SELECT tag_name FROM tag WHERE tag_name = "{}"
            '''.format(tag_name)
        )

        if len(tag_data) > 0:
            tag_name = tag_data[0][0]
            human_readable_tag = utils.make_decoded(tag_data[0][0])

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

    def remove_tags_from_photo(self, photo_id, tag_list=None):
        """
        Accepts a photo_id as an int and optional list of tag_names.

        If a tag_list is given then only the specified tags are removed from the photo_tag table.

        If no tag_name is not given all tags associated with the photo from the photo_tag table are removed.
        """
        if tag_list is not None:
            for tag in tag_list:
                self.db.make_query(
                    '''
                    DELETE FROM photo_tag
                    WHERE tag_name = "{}"
                    AND photo_id = {}
                    '''.format(utils.make_encoded(tag), photo_id)
                )
        else:
            self.db.make_query(
                '''
                DELETE FROM photo_tag
                WHERE photo_id = {}
                '''.format(photo_id)
            )

    def get_tag_photos_in_range(self, tag_name, limit=20, offset=0):
        """
        Returns a dict of dicts with photo data within the limit and from the offset specified for the tag specified.
        """
        tag_name = utils.make_encoded(tag_name)

        # Get all photos associated with the tag name.
        num_photos = self.count_photos_by_tag_name(tag_name)

        if offset > num_photos:
            offset = num_photos - (num_photos % 20)

        page = offset // limit

        pages = num_photos // limit

        # Make the pages count start at 1.
        if num_photos == 20:
            page = 1
            pages = 1
        else:
            page += 1
            pages += 1

        data = self.db.get_query_as_list(
            '''
            SELECT photo_id, photo_title, views, date_taken, tag_name, large_square FROM photo
            JOIN photo_tag USING(photo_id)
            JOIN images USING(photo_id)
            WHERE tag_name = "{}"
            ORDER BY date_taken
            DESC LIMIT {} OFFSET {}
            '''.format(tag_name, limit, offset)
        )

        # Decode the title.
        for photo in data:
            if photo['photo_title'] is not None:
                photo['photo_title'] = utils.make_decoded(
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
        rtn_dict['human_readable_name'] = utils.make_decoded(tag_name)
        rtn_dict['page'] = page
        rtn_dict['pages'] = pages

        rtn_dict['tag_info'] = {
            'number_of_photos': self.count_photos_by_tag_name(tag_name)
        }

        return rtn_dict

    def update_tag(self, new_tag, old_tag):
        """
        Replaces the old_tag with the new_tag.

        Updated all the photos using the tag in the photo_tag table.

        It encodes the tags first.
        """
        # Encode the tags.
        new_tag = utils.make_encoded(new_tag)
        old_tag = utils.make_encoded(old_tag)

        # Add the new tag to the tag table.
        self.add_tag(new_tag)

        # Update photo_tag to replace the old tag with the new tag.
        self.db.make_query(
            '''
            UPDATE photo_tag
            SET tag_name = "{}"
            WHERE tag_name = "{}"
            '''.format(new_tag, old_tag)
        )

        # Remove the old_tag.
        self.remove_tag_name(old_tag)

        # Update the tag count for the new tag.
        self.update_photo_count(new_tag)

        return self.get_tag(new_tag)


if __name__ == "__main__":
    pt = PhotoTag()

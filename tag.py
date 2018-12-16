import urllib.parse
import sqlite3


from database_interface import Database


class Tag(object):

    def __init__(self):
        self.db = Database('eigi-data.db')

    def check_all_tag_photo_counts(self):
        """
        Gets a count of all the photos associated with a tag.
        Checks that the photos column in tag is up to date.
        """
        data = self.db.get_query_as_list(
            '''
            select * from tag
            '''
        )

        for tag in data:
            print()
            print(tag)
            # query for the number of photos using the tag
            # compare it to the number in the photos column
            # update if necessary
            query_count = self.db.get_query_as_list(
                '''
                select count(tag_name)
                from photo_tag
                where tag_name = "{}"
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

    def update_photo_count(self, tag_name):
        """
        Updates the photo count for the given tag.
        """
        # query_count = self.db.get_query_as_list(
        #     '''
        #         select count(tag_name)
        #         from photo_tag
        #         where tag_name = "{}"
        #         '''.format(tag_name)
        # )

        count = self.get_photo_count_by_tag(tag_name)

        self.db.make_query(
            '''
            update tag
            set photos = {}
            where tag_name = "{}"
            '''.format(count, tag_name)
        )

    def tag_photo_count(self):
        """
        Gets a count of all the photos associated with a tag.
        Checks that the photos column in tag is up to date.
        """
        data = self.db.get_query_as_list(
            '''
            select * from tag
            '''
        )

        # print(data)

        for tag in data:
            print()
            print(tag)
            # query for the number of photos using the tag
            # compare it to the number in the photos column
            # update if necessary
            query_count = self.db.get_query_as_list(
                '''
                select count(tag_name)
                from photo_tag
                where tag_name = "{}"
                '''.format(tag['tag_name'])
            )

            # print(query_count)

            if query_count[0]['count(tag_name)'] == tag['photos']:
                print('OK', 'actual photos number with tag',
                      query_count[0]['count(tag_name)'], 'in photos column', tag['photos'])
            else:
                print('MISSMATCH IN PHOTOS AND PHOTOS WITH TAG\n', 'actual photos number with tag',
                      query_count[0]['count(tag_name)'], 'in photos column', tag['photos'])
                break

    def check_forbidden(self, tag_name):
        print('hello from check_forbidden')
        print(tag_name)

        forbidden = [";", "/", "?", ":", "@", "=", "&", '"', "'", "<", ">",
                     "#", "%", "{", "}", "|", "\\", "/", "^", "~", "[", "]", "`"]
        for char in tag_name:
            if char in forbidden:
                return urllib.parse.quote(tag_name, safe='')

        return tag_name

    def decode_tag(self, tag_name):
        return urllib.parse.unquote(tag_name)

    def get_all_tags(self):
        # as a list of dict values
        tag_data = self.db.get_query_as_list(
            "SELECT tag_name, photos FROM tag order by tag_name"
        )

        rtn_dict = {

        }

        count = 0
        for tag in tag_data:
            rtn_dict[count] = tag
            tag_name = tag['tag_name']
            # adding the number of photos with the tag
            rtn_dict[count]['photos'] = tag['photos']
            rtn_dict[count]['human_readable_tag'] = self.decode_tag(
                tag['tag_name'])
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
        for tag in tag_data:
            # print(self.decode_tag(tag['tag_name']))

            tag['human_readable_tag'] = self.decode_tag(tag['tag_name'])

        # print(tag_data)

        return tag_data

    def get_photo_count_by_tag(self, tag_name):
        query_string = '''
            select count(photo_id) from photo
            join photo_tag using(photo_id)
            where tag_name = "{}"
        '''.format(tag_name)

        photo_count = self.db.get_query_as_list(query_string)

        if len(photo_count) > 0:
            return photo_count[0]['count(photo_id)']

    def get_photos_by_tag(self, tag_name):
        """
        Get all the photos that are associated with a particular tag.

        I will need to handle spaces.
        """
        # q_data = None

        query_string = '''
            select photo_id, photo_title, views, tag_name, large_square from photo
            join photo_tag using(photo_id)
            join images using(photo_id)
            where tag_name = "{}"
            order by views desc
        '''.format(tag_name)

        tag_data = self.db.get_query_as_list(query_string)

        # print(tag_data)

        rtn_dict = {
            'tag_info': {'number_of_photos': self.get_photo_count_by_tag(tag_name)}
        }

        count = 0
        for t in tag_data:
            rtn_dict[count] = t
            count += 1

        return rtn_dict

    def get_tag(self, tag_name):
        tag_data = self.db.make_query(
            '''
            select tag_name from tag where tag_name = "{}"
            '''.format(tag_name)
        )

        return tag_data

    def check_photo_tag(self, tag_name):
        data = self.db.make_query(
            '''select * from photo_tag where tag_name = "{}" '''
            .format(tag_name))

        if len(data) > 0:
            return True
        return False

    def remove_tag_name(self, tag_name):
        if '%' in tag_name:
            tag_name = urllib.parse.quote(tag_name, safe='')
        self.db.make_query(
            '''
            delete from tag where tag_name = "{}"
            '''.format(tag_name)
        )

        self.db.make_query(
            '''
            delete from photo_tag where tag_name = "{}"
            '''.format(tag_name)
        )

        self.update_photo_count(tag_name)

    def delete_tag(self, tag_name):
        # you have to remove the tag from the tag table
        self.db.delete_rows_where('tag', 'tag_name', tag_name)
        # and also in photo_tag
        self.db.delete_rows_where('photo_tag', 'tag_name', tag_name)

        if not self.get_tag(tag_name) and not self.check_photo_tag(tag_name):
            return True
        else:
            return False

    def clean_tags(self):
        forbidden = ['  ', ';']
        # as a list of dict values
        tag_data = self.db.get_query_as_list("SELECT * FROM tag")
        for tag in tag_data:
            print(tag['tag_name'], tag['tag_name'] in forbidden)
            if tag['tag_name'] in forbidden:
                print('please just ket me die already, ', tag['tag_name'])
                self.remove_tag_name(tag['tag_name'])

        tag_data = self.db.get_query_as_list("SELECT * FROM photo_tag")
        for tag in tag_data:
            print(tag['tag_name'], tag['tag_name'] in forbidden)
            if tag['tag_name'] in forbidden:
                print('please just ket me die already, ', tag['tag_name'])
                self.remove_tag_name(tag['tag_name'])

    def remove_tags_from_photo(self, photo_id, tag_list):
        for tag in tag_list:
            print(tag)

            # if the tag isn't present it will just fail silently
            resp = self.db.make_query(
                '''
                delete from photo_tag 
                where photo_id = {}
                and tag_name = "{}"
                '''.format(photo_id, tag)
            )
            print(resp)

            self.update_photo_count(tag)

    def add_tags_to_photo(self, photo_id, tag_list):
        print('add_tags_to_photo', tag_list)

        # for i in range(len(tag_list)):
        #     tag_list[i] = urllib.parse.quote(tag_list[i], safe='')
        #     print(tag_list[i],
        #           'parsed', urllib.parse.unquote(tag_list[i]), tag_list)

        # for each tag
        # check if the tag is in the database already
        # if it is not then add it to the tag table
        for tag in tag_list:

            # will return None if the tag is not in the tag table
            # tag_name is the column name
            data = self.db.get_row('tag', 'tag_name', tag)

            print('data is', data)

            if data is None:
                print('should not get here')

                print(tag)
                print('that value is not in the db')

                self.db.insert_data(
                    table='tag',
                    tag_name=tag,
                    user_id='28035310@N00',
                    photos=self.get_photo_count_by_tag(tag)
                )

                print('should be added now...\n')

                if self.db.get_row('tag', 'tag_name', tag):
                    print('added tag, ', tag)

            # The tag is now in the database.

            # Does return 0 if there are no pictures using the tag.
            # print(self.get_photo_count_by_tag(tag))

            # add the tag to the table photo_tag
            resp = self.db.insert_data(
                table='photo_tag',
                photo_id=photo_id,
                tag_name=tag,
            )

        data = self.db.make_query(
            '''
            select * from photo_tag where photo_id = {}
            '''.format(photo_id)
        )

        tags_in_data = []
        if len(data) > 0:
            for tag in data:
                tags_in_data.append(tag[1])

        print(tags_in_data)
        for tag in tag_list:
            if tag not in tags_in_data:
                return False
            else:
                self.update_photo_count(tag)

        return True

    def update_tag(self, new_tag, old_tag):
        print('hello from update_tag - passed values, ', new_tag, old_tag)
        # check if new tag exists
        test = self.db.make_query(
            '''
            select * from tag where tag_name = "{}"
            '''.format(new_tag)
        )

        # print(test)

        if not test:
            # if the tag doesn't exist already then update it
            # existing tag to the new tag
            self.db.make_query(
                '''
                update tag
                set tag_name = "{}"
                where tag_name = "{}"
                '''.format(new_tag, old_tag)
            )

        # if new tag exists or not you have to update photo_tag
        self.db.make_query(
            '''
            update photo_tag
            set tag_name = "{}"
            where tag_name = "{}"
            '''.format(new_tag, old_tag)
        )

        # update the photo count for the tag table
        self.update_photo_count(new_tag)

        if self.get_tag(new_tag) and not self.get_tag(old_tag):
            return True
        else:
            return False


if __name__ == "__main__":
    t = Tag()

    t.clean_tags()

    # t.get_photo_tags(31734289038)

    # t.update_photo_count('365')

    # print(t.update_tag('mars', 'aberdeen'))

    # print(t.get_all_tags())

    # print(t.add_tags_to_photo(44692598005, ['cheese']))

    # print(t.get_all_tags())

    # t.update_tag('%23%london', "london")
    # t.update_tag_test('%23london', '#london')

    # t.get_photos_by_tag("21erh'aus")

    # this is now really slow?
    # cascade on update also means that if you don't add back for some reason you will lose all those tags
    # so it's way more dangerous
    # new tag, old tag
    # print(t.update_tag("test", "london"))
    # print(t.update_photo_count('london'))

    # print(t.update_tag())
    # t.update_tag('london', 'cheese')

    # t.tag_photo_count()
    # t.check_tag_photo_count()

    # t.update_photo_count('manchester')
    # t.get_all_tags()

    # {'photoId': '31734289628', 'selectedTags': ['donaupark']}
    # t.remove_tags_from_photo('31734289628', ['donaupark', 'cheese'])

    # print(t.get_photo_count_by_tag('people'))

    # print(t.get_all_tags())

    # print(t.get_all_tags_without_count())

    # print(t.get_photo_count_by_tag('vienna'))

    # t.clean_tags()

    # print(t.add_tags_to_photo('3400128875', ['test tag name', 'test tag two']))

    # print(t.get_photo_tags('5052576689'))

    # print(t.get_all_tags())

    # This is actually a special case as the new_name is for an existing tag

    # new then old
    # print(t.update_tag('cafe shop', 'cafe'))

    # print(t.delete_tag('test'))

    # print(t.check_photo_tag('test'))

    # print(t.get_photos_by_tag('apples'))
    # print(t.get_photo_tags(5052580779))

    # print(t.get_photo_count_by_tag('apples'))

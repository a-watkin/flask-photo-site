from database_interface import Database
import sqlite3


class Tag(object):

    def __init__(self):
        self.db = Database('eigi-data.db')

    def get_all_tags_without_count(self):
        # as a list of dict values
        tag_data = self.db.get_query_as_list("SELECT tag_name FROM tag")

        rtn_dict = {

        }

        count = 0
        for tag in tag_data:
            rtn_dict[count] = tag
            tag_name = tag['tag_name']
            # adding the number of photos with the tag
            # it's slow here because each tag means a query to the db
            # rtn_dict[count]['photos'] = self.get_photo_count_by_tag(
            #     tag['tag_name'])
            count += 1

        return rtn_dict

    def update_tag_photo_count(self):
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
                where tag_name = '{}'
                '''.format(tag['tag_name'])
            )

            # print(query_count)

            if query_count[0]['count(tag_name)'] == tag['photos']:
                print('OK', 'actual photos number with tag',
                      query_count[0]['count(tag_name)'], 'in photos column', tag['photos'])
            else:
                print('MISSMATCH IN PHOTOS AND PHOTOS WITH TAG\n', 'actual photos number with tag',
                      query_count[0]['count(tag_name)'], 'in photos column', tag['photos'])

                tag_name = tag['tag_name']
                count = query_count[0]['count(tag_name)']

                # Updating
                print('UPDATING')
                self.db.make_query(
                    '''
                    update tag 
                    set photos = {}
                    where tag_name = '{}'
                    '''.format(count, tag_name)
                )

                print(tag_name, count)
                break

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
                where tag_name = '{}'
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

    def get_all_tags(self):
        """
        DANGER!
        Now getting count of photos for the tag from the database.
        """
        # as a list of dict values
        tag_data = self.db.get_query_as_list(
            "SELECT tag_name, photos FROM tag order by tag_name")

        # print(tag_data)

        rtn_dict = {

        }

        count = 0
        for tag in tag_data:
            rtn_dict[count] = tag
            tag_name = tag['tag_name']
            # adding the number of photos with the tag
            # it's slow here because each tag means a query to the db
            rtn_dict[count]['photos'] = tag['photos']

            count += 1

        # print(rtn_dict)
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
        query_string = '''
            select count(photo_id) from photo
            join photo_tag using(photo_id)
            where tag_name = '{}'
        '''.format(tag_name)

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

    def get_tag(self, tag_name):
        tag_data = self.db.make_query(
            '''
            select tag_name from tag where tag_name = '{}'
            '''.format(tag_name)
        )

        return tag_data

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
            self.db.insert_data(
                table='tag',
                tag_name=new_tag,
                user_id='28035310@N00'
            )

        # otherwise the new_tag is in the tag table and doesn't need to be added

        # insert new tag into photo_tag
        self.db.insert_tag_data('photo_tag', new_photo_tag_data)

        # it doesn't cascade on delete so delete the old tag
        self.db.delete_rows_where('tag', 'tag_name', old_tag)

        # delete the old tag from photo_tag
        self.db.delete_rows_where('photo_tag', 'tag_name', old_tag)

        # confirm that the new tag is present and the old tag is not
        if self.get_tag(new_tag) and not self.get_tag(old_tag):
            return True
        else:
            return False

    def check_photo_tag(self, tag_name):
        data = self.db.make_query(
            '''select * from photo_tag where tag_name = '{}' '''
            .format(tag_name))

        if len(data) > 0:
            return True
        return False

    def delete_tag(self, tag_name):
        # you have to remove the tag from the tag table
        self.db.delete_rows_where('tag', 'tag_name', tag_name)
        # and also in photo_tag
        self.db.delete_rows_where('photo_tag', 'tag_name', tag_name)

        if not self.get_tag(tag_name) and not self.check_photo_tag(tag_name):
            return True
        else:
            return False

    def add_tags_to_photo(self, photo_id, tag_list):
        print('add_tags_to_photo', tag_list)

        # iterate over the list of tags

        # for each tag
        # check if the tag is in the database already
        # if it is not then add it to the tag table
        for tag in tag_list:

            # will return None if the tag is not in the tag table
            # tag_name is the column name
            data = self.db.get_row('tag', 'tag_name', tag)

            if data is None:

                print(tag)
                print('that value is not in the db')

                self.db.insert_data(
                    table='tag',
                    tag_name=tag,
                    user_id='28035310@N00'
                )

                print('should be added now...\n')

                if self.db.get_row('tag', 'tag_name', tag):
                    print('added tag, ', tag)

            # so now the tag should be in the table tag
            # already present or added

            # add the tag to the table photo_tag
            self.db.insert_data(
                table='photo_tag',
                photo_id=photo_id,
                tag_name=tag
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

        return True

    def remove_tag_name(self, tag_name):
        self.db.make_query(
            '''
            delete from tag where tag_name = '{}'
            '''.format(tag_name)
        )

    def clean_tags(self):
        forbidden = [' ', ';']
        # as a list of dict values
        tag_data = self.db.get_query_as_list("SELECT tag_name FROM tag")
        for tag in tag_data:
            tag_name = tag['tag_name']

            if len(tag_name) == 1:
                self.remove_tag_name(tag_name)

            if tag_name in forbidden:
                self.remove_tag_name(tag_name)

    def remove_tags_from_photo(self, photo_id, tag_list):
        for tag in tag_list:
            print(tag)

            # if the tag isn't present it will just fail silently
            resp = self.db.make_query(
                '''
                delete from photo_tag
                where photo_id = {}
                and tag_name = '{}'
                '''.format(photo_id, tag)
            )
            print(resp)


if __name__ == "__main__":
    t = Tag()

    # t.tag_photo_count()
    t.update_tag_photo_count()
    # t.get_all_tags()

    # {'photoId': '31734289628', 'selectedTags': ['donaupark']}
    # t.remove_tags_from_photo('31734289628', ['donaupark', 'cheese'])

    # print(t.get_photo_count_by_tag('people'))

    # print(t.get_all_tags())

    # print(t.get_all_tags_without_count())

    # print(t.get_photo_count_by_tag('vienna'))

    # t.clean_tags()

    # print(t.add_tags_to_photo('3400128875', ['test tag name', 'test tag two']))

    # print(t.get_photo_tags('3400128875'))

    # print(t.get_all_tags())

    # This is actually a special case as the new_name is for an existing tag

    # new then old
    # print(t.update_tag('cafe shop', 'cafe'))

    # print(t.delete_tag('test'))

    # print(t.check_photo_tag('test'))

    # print(t.get_photos_by_tag('apples'))
    # print(t.get_photo_tags(5052580779))

    # print(t.get_photo_count_by_tag('apples'))

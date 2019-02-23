from database_interface import Database
import json


class DateTimeFix(object):

    def __init__(self):
        self.db = Database('eigi-data.db')

    def update_datetime_taken(self, photo_id, datetime_taken):
        pass

    """
    There are three types of record.

    1. Exif data and a photo associated to it.

    2. A different kind of Exif data and an associated photo.

    3. Exif data without an associated photo. This situation should already be prevented in future.
    """

    def get_photo_by_id(self, photo_id):
        return self.db.get_query_as_list(
            '''
            select * from photo where photo_id = {}
            '''.format(photo_id)
        )

    def read_exif_datetime(self):
        exif_data = self.db.get_query_as_list(
            '''
            select * from exif
            '''
        )

        problem_list = []

        for x in exif_data:
            photo_id = None
            original_datetime = None

            exif = json.loads(x['exif_data'])

            # print(x)

            try:
                photo_id = exif['photo']['id']
                for f in exif['photo']['exif']:
                    if f['tag'] == 'DateTimeOriginal':
                        data = f['tag']
                        original_datetime = f['raw']['_content']

                # print()
                # print(photo_id)
                # print(original_datetime)
                # print()

            except Exception as e:
                # alternate exif data format
                # print('problem, ', x['photo_id'])
                problem_list.append(x['photo_id'])
                pd = json.loads(x['exif_data'])
                try:
                    # print()
                    # print(pd.keys())

                    data = self.db.get_query_as_list(
                        '''
                        select photo_id, date_taken from photo where photo_id = '{}'
                        '''.format(x['photo_id'])
                    )

                    # print(data)

                    if data:
                        if pd['EXIF DateTimeOriginal'] == data[0]['date_taken']:
                            print('OK')
                        else:
                            print('not ok, ', data)

                    print(x['photo_id'], pd['EXIF DateTimeOriginal'])

                except Exception as e:
                    # print('eh ', x['photo_id'])

                    try:
                        problem_data = self.db.get_query_as_list(
                            '''
                            select * from photo where photo_id = {}
                            '''.format(x['photo_id'])
                        )

                        # these are mostly exif data rows for photos that don't exist
                        # print('here? ', x['photo_id'], problem_data)

                        print()
                        print('grr \n', x.keys())
                        print(x['exif_id'])

                        if not isinstance(x['exif_id'], dict):
                            if self.get_photo_by_id(x['exif_id']):
                                print('exif_id sometimes photo id')
                                print(self.get_photo_by_id(x['exif_id']))
                                break

                        if not isinstance(x['photo_id'], dict):
                            if self.get_photo_by_id(x['photo_id']):
                                print('photo_id value sometimes photo id')
                                print(self.get_photo_by_id(x['photo_id']))
                                break

                        print('photo_id value sometimes photo id')
                        print(self.get_photo_by_id(x['photo_id']))

                        print()

                        print(x['exif_data'])
                        print(x['photo_id'])
                        print()
                        if x['exif_data']:
                            print(x['exif_data'])

                        # if len(problem_data) > 0:
                        #     self.db.make_query(
                        #         '''
                        #         UPDATE photo
                        #         SET date_taken = "{}"
                        #         WHERE photo_id = "{}";
                        #         '''.format()
                        #     )

                    except Exception as e:
                        print()
                        print('photo_id is, ',
                              x['photo_id'], 'exif_id', x['exif_id'], x.keys())
                        print('really big problem ', e, '\n')
                        print()

        # for x in problem_list:
        #     try:
        #         problem_data = self.db.get_query_as_list(
        #             '''
        #             select * from photo where photo_id = {}
        #             '''.format(x)
        #         )

        #         if len(problem_data) > 0:
        #             print(problem_data)
        #         else:
        #             print('no data for this photo_id ', x)

        #     except Exception as e:
        #         print(x, '\n', e)

    def remove_invalid_exif_rows(self):
        exif_data = self.db.get_query_as_list(
            '''
            select * from exif
            '''
        )

        """
        exif_id is sometimes longer than 10 but mostly 10

        photo_id is 10 sometimes 11

        exif data is always long
        """
        for d in exif_data:
            # Removing exif rows not associated with photos
            if len(d['photo_id']) > 11:
                print()
                print(d['exif_data'])
                if self.get_photo_by_id(d['exif_data']):
                    print(self.get_photo_by_id(d['exif_data']))
                else:
                    self.db.make_query(
                        '''
                        delete from exif where photo_id = '{}'
                        '''.format(d['photo_id'])
                    )

            # these records also had no photos associated with them
            if '{' in d['exif_id']:
                print()
                print(d['photo_id'])
                if self.get_photo_by_id(d['photo_id']):
                    print(self.get_photo_by_id(d['photo_id']))
                else:
                    self.db.make_query(
                        '''
                        delete from exif where photo_id = '{}'
                        '''.format(d['photo_id'])
                    )

            # records where exif data is empty
            if len(d['exif_data']) < 10:
                if self.get_photo_by_id(d['photo_id']):
                    print(self.get_photo_by_id(d['photo_id']))
                else:
                    self.db.make_query(
                        '''
                        delete from exif where photo_id = '{}'
                        '''.format(d['photo_id'])
                    )

    def check_exif_photo(self):
        pass


if __name__ == "__main__":
    dtf = DateTimeFix()
    # dtf.read_exif_datetime()

    # remove invalid exif data, invalid format and not associated with a photo
    # dtf.remove_invalid_exif_rows()

    # check that exif data related to a photo
    dtf.check_exif_photo()

from database_interface import Database
import json


class DateTimeFix(object):

    def __init__(self):
        self.db = Database('eigi-data.db')

    def get_exif_rows(self):
        """
        Returns all the exif rows as a list of dicts.
        """
        return self.db.get_query_as_list(
            '''
            select * from exif
            '''
        )

    def get_photo_by_id(self, photo_id):
        """
        Returns all the photo rows that correspond to the given photo_id.
        """
        try:
            return self.db.get_query_as_list(
                '''
            select * from photo where photo_id = "{}"
            '''.format(photo_id)
            )
        except Exception as e:
            print('No photo data found for this photo_id ', e)
            return []

    def get_exif_data_by_id(self, exif_id):
        """
        Returns all the exif rows that correspond to the given exif_id.
        """
        try:
            return self.db.get_query_as_list(
                '''
                select * from exif where exif_id = {}
                '''.format(exif_id)
            )

        except Exception as e:
            print('No exif value found for this exif_id ', e)
            return []

    def switich_exif_data_id(self):
        """
        Switches exif_data and exif_id if they are in the wrong order.

        This only works if the exif_data is in exif_id column.
        """
        # 2600028293
        # photo id is ok, but exif_data and id are switched
        exif_data = self.get_exif_rows()

        for d in exif_data:
            if len(d['exif_id']) > len(d['exif_data']):
                # print('probs')
                exif_id = d['exif_data']
                exif_data = d['exif_id']

                self.db.make_sanitized_query(
                    '''
                    update exif
                    set exif_id = ?, exif_data = ?
                    where photo_id = ?
                    ''', (exif_id, exif_data, d['photo_id'])
                )

    def check_len_exif_id(self):
        exif_data = self.get_exif_rows()

        for d in exif_data:
            if len(d['exif_id']) > 11:
                print(d['exif_id'], '\n', d['photo_id'], '\n', d['exif_data'])

    def check_photo_id(self):
        """
        Checks that the values in the photo_id field of the exif data relate to a photo in the photo table.
        """
        # get all exif rows
        exif_data = self.get_exif_rows()

        probs = []
        for d in exif_data:
            photo_data = self.get_photo_by_id(d['photo_id'])
            if photo_data:
                print('ok')
            else:
                print('\n PROBLEMS', d['photo_id'])
                probs.append(d['photo_id'])

        print()
        print('check photo id probs, ', probs)
        print(len(probs))

    def check_photo_exif_ids(self):
        exif_data = self.get_exif_rows()

        problems = []
        for d in exif_data:
            if self.get_photo_by_id(d['photo_id']) or self.get_photo_by_id(d['exif_id']):
                if not self.get_photo_by_id(d['photo_id']):
                    exif_id = d['photo_id']
                    photo_id = d['exif_id']

                    self.db.make_sanitized_query(
                        '''
                        update exif
                        set exif_id = ?, photo_id = ?
                        where photo_id = ?
                        ''', (exif_id, photo_id, d['photo_id'])
                    )

                # print(self.get_photo_by_id(d['photo_id']))
            else:
                problems.append((d['exif_id'], d['photo_id']))

                self.db.make_query(
                    '''
                    delete from exif where exif_id = "{}"
                    '''.format(d['exif_id'])
                )

        print(problems, '\n', len(problems))

    def update_photo_datetime_taken(self):
        """
        Updates the photo date_taken field using the original datetime taken from the exif data.
        """
        exif_data = self.get_exif_rows()

        for d in exif_data:
            print(d['photo_id'])
            try:
                e_data = json.loads(d['exif_data'])
                # print(e_data.keys())
                for x in e_data['photo']['exif']:
                    if 'DateTimeOriginal' in x.values():
                        print(x['raw']['_content'], '\n')
                        datetime_taken = x['raw']['_content']
                        print(self.update_date_taken(
                            d['photo_id'], datetime_taken))

            except Exception as e:
                e_data = json.loads(d['exif_data'])
                # print(e_data.keys())
                print(e_data['EXIF DateTimeOriginal'])

                print(self.update_date_taken(
                    d['photo_id'], e_data['EXIF DateTimeOriginal']))

    def update_date_taken(self, photo_id, datetime_string):
        return self.db.make_sanitized_query(
            '''
            update photo
            set date_taken = ?
            where photo_id = ?
            ''', (datetime_string, photo_id)
        )


if __name__ == "__main__":
    dtf = DateTimeFix()
    # swtich exif_id and exif_data if in incorrect order
    dtf.switich_exif_data_id()

    # try both exif_id and photo_id against photo table
    # if nothing found remove exif recrod
    dtf.check_photo_exif_ids()

    # this seems sort of pointless? it's ok as a final check
    dtf.check_photo_id()

    # check the length of exif_id, there's one row that has a longer than usual exif_id that was causing a problem
    # now resolved
    dtf.check_len_exif_id()

    # update the photo table with the original time taken value from the exif data
    dtf.update_photo_datetime_taken()

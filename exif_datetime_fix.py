from database_interface import Database
import json


class DateTimeFix(object):

    def __init__(self):
        self.db = Database('eigi-data.db')

    def get_photo_by_id(self, photo_id):
        return self.db.get_query_as_list(
            '''
            select * from photo where photo_id = "{}"
            '''.format(photo_id)
        )

    def get_exif_data_by_id(self, exif_id):
        try:
            exif_data = self.db.get_query_as_list(
                '''
                select * from exif where exif_id = {}
                '''.format(exif_id)
            )

            if exif_data:
                return exif_data

        except Exception as e:
            return []

    def test_row(self):
        # 2600028293
        # photo id is ok, but exif_data and id are switched
        # print(self.get_photo_by_id(2600028293))

        exif_data = self.db.get_query_as_list(
            '''
            select * from exif
            '''
        )

        for d in exif_data:
            if len(d['exif_id']) > 11:
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

    def check_photo_id(self):
        exif_data = self.db.get_query_as_list(
            '''
            select * from exif
            '''
        )

        for d in exif_data:
            try:
                print('trying with value ', d['photo_id'])
                photo_data = self.get_photo_by_id(d['photo_id'])
                print('\n', photo_data)
            except Exception as e:
                print('problem ', e)
                print(d['photo_id'], '\n', d['exif_data'], '\n', d['exif_id'])

                if len(d['exif_id']) > 11:
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
        exif_data = self.db.get_query_as_list(
            '''
            select * from exif
            '''
        )

        for d in exif_data:
            if len(d['exif_id']) > 11:
                print(d['exif_id'], d['photo_id'])

    def check_photo_id(self):
        exif_data = self.db.get_query_as_list(
            '''
            select * from exif
            '''
        )

        probs = []
        for d in exif_data:
            photo_data = self.get_photo_by_id(d['photo_id'])
            if photo_data:
                print('ok')
            else:
                print('\n PROBLEMS', d['photo_id'])
                probs.append(d['photo_id'])

        print()
        print(probs)
        print(len(probs))

    def check_len_photo_id(self):
        exif_data = self.db.get_query_as_list(
            '''
            select * from exif
            '''
        )

        count = 0
        for d in exif_data:
            if len(d['photo_id']) > 11:
                print()
                print(d['exif_id'], d['exif_data'])
                count += 1

                photo_data = self.get_photo_by_id(d['exif_id'])
                print('phto_data ', photo_data)

                self.db.make_query(
                    '''
                    delete from exif where exif_id = {}
                    '''.format(d['exif_id'])
                )

        print(count)

    def check_photo_exif_ids(self):
        exif_data = self.db.get_query_as_list(
            '''
            select * from exif
            '''
        )

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

        # if self.get_photo_by_id(d['exif_id']):
        #     print(self.get_photo_by_id(d['exif_id']))


if __name__ == "__main__":
    dtf = DateTimeFix()
    # dtf.test_row()
    dtf.check_photo_id()
    # dtf.check_len_exif_id()
    # dtf.check_len_photo_id()

    # dtf.check_photo_exif_ids()

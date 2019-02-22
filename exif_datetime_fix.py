from database_interface import Database
import json


class DateTimeFix(object):

    def __init__(self):
        self.db = Database('eigi-data.db')

    def update_datetime_taken(self, photo_id, datetime_taken):
        pass

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
                # print('problem, ', x['photo_id'])
                problem_list.append(x['photo_id'])
                pd = json.loads(x['exif_data'])
                try:
                    # print(pd.keys())
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
                        print('here? ', x['photo_id'], problem_data)

                        if len(problem_data) > 0:
                            self.db.make_query(
                                '''
                                update
                                '''
                            )

                    except Exception as e:
                        print('really big problem ', e, '\n', x['photo_id'])

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


if __name__ == "__main__":
    dtf = DateTimeFix()
    dtf.read_exif_datetime()

from database_interface import Database
import sqlite3


class Photos(object):

    def __init__(self):
        self.db = Database('eigi-data.db')

    def get_photos_in_range(self, limit=20, offset=0):
        """
        Returns the latest 10 photos.

        Offset is where you want to start from, so 0 would be from the most recent.
        10 from the tenth most recent etc.
        """
        q_data = None
        with sqlite3.connect(self.db.db_name) as connection:
            c = connection.cursor()

            c.row_factory = sqlite3.Row

            query_string = (
                '''select photo_id, views, photo_title, date_uploaded, date_taken, images.large_square from photo
                join images using(photo_id)
                order by date_uploaded
                desc limit {} offset {}'''
            ).format(limit, offset)

            q_data = c.execute(query_string)

        rtn_dict = {
            'limit': limit,
            'offset': offset,
            'photos': []
        }

        """
        I think it may actually be better to layout what fields you want here.

        And maybe include all sizes.
        """

        data = [dict(ix) for ix in q_data]

        a_dict = {}
        count = 0
        for d in data:
            a_dict[count] = d
            count += 1

        rtn_dict = {'photos': a_dict}

        rtn_dict['limit'] = limit
        rtn_dict['offset'] = offset

        return rtn_dict

        # for d in data:
        #     rtn_dict['photos'].append(d)

        # return rtn_dict

        # rtn_dict =
        # count = 0
        # for row in q_data:
        #     print(rtn_dict)
        #     rtn_dict[count] = [dict(ix) for ix in q_data]
        #     count += 1

        # rtn_dict['limit'] = limit
        # rtn_dict['offset'] = offset

        # return rtn_dict


if __name__ == "__main__":
    p = Photos()
    print(p.get_photos_in_range())
    # print(p.db.db_name)

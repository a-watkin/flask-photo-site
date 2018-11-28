from database_interface import Database
import sqlite3


class Album(object):

    def __init__(self):
        self.db = Database('eigi-data.db')

    def get_albums(self):
        """
        Returns all albums.
        """
        album_data = self.db.get_query_as_list(
            "select * from album;"
        )

        # get the album id
        # print(album_data)

        # I also need an image to represent the album

        rtn_dict = {

        }

        count = 0
        for album in album_data:
            # print('\n', 'album_id', album['album_id'])
            album_dover_dict = self.get_album_cover(album['album_id'])
            album['large_square'] = album_dover_dict[0]['large_square']
            rtn_dict[count] = album
            count += 1

        return rtn_dict

    def get_containing_album(self, photo_id):
        query_string = '''

                select album.album_id, album.title, album.views, album.description, album.photos, date_created 
                from photo_album
                join album on(photo_album.album_id=album.album_id)
                where photo_album.photo_id={}

        '''.format(photo_id)

        album_data = self.db.get_query_as_list(
            query_string
        )

        return album_data

    # query string for getting the large_square photo for the album cover

    def get_album_cover(self, album_id):
        query_string = '''
                            select images.large_square from album
                            join photo_album on(album.album_id=photo_album.album_id)
                            join photo on(photo_album.photo_id=photo.photo_id)
                            join images on(images.photo_id=photo.photo_id)
                            where album.album_id={}
                            order by photo.date_uploaded asc limit 1
                        
                        '''.format(album_id)

        album_cover = self.db.get_query_as_list(query_string)

        # print(album_cover)

        return album_cover

    def get_album_photos(self, album_id):
        query_string = '''
                select album.title, album.album_id, 
                album.description, album.views, album.photos,  
                images.large_square,
                images.original,
                photo.photo_id, photo.date_taken,
                photo.photo_title, photo.date_uploaded,  photo.views
                from album
                join photo_album on(album.album_id=photo_album.album_id)
                join photo on(photo_album.photo_id=photo.photo_id)
                join images on(images.photo_id=photo.photo_id)
                where album.album_id={}
                order by photo.date_uploaded asc
                '''.format(album_id)

        album_data = self.db.get_query_as_list(
            query_string
        )

        rtn_dict = {

        }

        count = 0
        for d in album_data:
            rtn_dict[count] = d
            count += 1

        return rtn_dict


if __name__ == "__main__":
    a = Album()
    # print(a.get_album_cover('72157650725849398'))
    # blah = a.get_albums()

    # print(blah.keys(), blah[0]['large_square'])

    # print(a.get_album_photos('72157650725849398'))

    print(a.get_containing_album(16748114355))

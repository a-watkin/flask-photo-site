from uploaded_photos import UploadedPhotos


up = UploadedPhotos()

print(up.user_id)

up.save_photo(
    2429676859, '2018-12-09 21:16:43.708922', '/2018/12/test_landscape_ba5f22cc.jpg', '/2018/12/test_landscape_ba5f22cc_lg_sqaure.jpg'
)

from django.test import TestCase
from unittest import mock


# Create your tests here.
class CartOperationTests(TestCase):
    def setUp(self):
        # self.hotel_api_res = {
        #     "resultCode": "00",
        #     "rootCause": "房型庫存查詢正確",
        #     "roomList": [
        #         {
        #             "hotelID": "138",
        #             "hotelName": "TEST_和逸飯店．高雄中山館",
        #             "roomID": "1C6102C3-CC95-4386-B61B-C816E1CAC8F3",
        #             "roomName": "舒適四人房(無窗:2大床)",
        #             "maxNoPerson": "4",
        #             "minNoPerson": "1",
        #             "stdNoPerson": "4",
        #             "count": "8",
        #             "invCount": "3"
        #         },
        #         {
        #             "hotelID": "138",
        #             "hotelName": "TEST_和逸飯店．高雄中山館",
        #             "roomID": "CFF4203F-CD78-4782-B9EB-2DE655A32E0C",
        #             "roomName": "舒適雙人\n房(無窗:1大床/2小床)",
        #             "maxNoPerson": "3",
        #             "minNoPerson": "1",
        #             "stdNoPerson": "2",
        #             "count": "3",
        #             "invCount": "0"
        #         },
        #     ]
        # }
        # self.hotels_api_res = {
        #                           "resultCode": "00",
        #                           "rootCause": "房型庫存查詢正確",
        #                           "roomList": [
        #                             {
        #                               "hotelID": "137",
        #                               "hotelName": "TEST_和逸飯店．台南西門館",
        #                               "roomID": "3992C545-5914-49F8-BD32-C97766C1BC75",
        #                               "roomName": "舒適客房(1大床/2小床)",
        #                               "maxNoPerson": "3",
        #                               "minNoPerson": "1",
        #                               "stdNoPerson": "2",
        #                               "count": "35",
        #                               "invCount": "30"
        #                             },
        #                             {
        #                               "hotelID": "137",
        #                               "hotelName": "TEST_和逸飯店．台南西門館",
        #                               "roomID": "4282640E-42CF-4BA3-A4AD-433B8DE7A837",
        #                               "roomName": "和逸四人房(2大床)",
        #                               "maxNoPerson": "4",
        #                               "minNoPerson": "1",
        #                               "stdNoPerson": "4",
        #                               "count": "35",
        #                               "invCount": "30"
        #                             },
        #                             {
        #                               "hotelID": "138",
        #                               "hotelName": "TEST_和逸飯店．高雄中山館",
        #                               "roomID": "1C6102C3-CC95-4386-B61B-C816E1CAC8F3",
        #                               "roomName": "舒適四人房(無窗:2大床)",
        #                               "maxNoPerson": "4",
        #                               "minNoPerson": "1",
        #                               "stdNoPerson": "4",
        #                               "count": "8",
        #                               "invCount": "3"
        #                             },
        #                             {
        #                               "hotelID": "138",
        #                               "hotelName": "TEST_和逸飯店．高雄中山館",
        #                               "roomID": "CFF4203F-CD78-4782-B9EB-2DE655A32E0C",
        #                               "roomName": "舒適雙人\n房(無窗:1大床/2小床)",
        #                               "maxNoPerson": "3",
        #                               "minNoPerson": "1",
        #                               "stdNoPerson": "2",
        #                               "count": "3",
        #                               "invCount": "0"
        #                             }
        #                           ]
        #                         }

    # one hotels
        pass

    @mock.patch("thsrcholidays.utils.requests.post")
    def test1_1_hotel_id(self, mock_post):
        Product.objects.create(id=11, thsrc_product_id="0", name="TEST_和逸飯店．高雄中山館2日自由行_New", loc="12", days_length=3)
        Hotel.objects.create(id=111, product_id=11, name="TEST_和逸飯店．高雄中山館", address="地址：80660高雄市前鎮區中山二路260號22-30樓")

        mock_post.return_value = mock.Mock(status=200, json=lambda **kwargs: self.hotel_api_res)

        product_obj = Product.objects.get(id=11)
        result = pmc.get_hotel_id(product_obj)

        # ordering result by db_id
        ordering = sorted([r["db_id"] for r in result])
        result = [
            {
                "success": r["success"],
                "res_id": r["res_id"],
                "db_id": r["db_id"],
            }
            for o in ordering for r in result if o == r["db_id"]
        ]
        expexted_result = [
            {
                "success": True,
                "res_id": "138",
                "db_id": 111,
            },
        ]
        self.maxDiff = None
        self.assertEqual(result, expexted_result)

# shopping cart api

## 使用前事先確認:
1. 丟過來的requests會先檢查 is_authenticated (django 內建功能)。
2. 如果是未登入的，則會去檢查requests中的cookie是否含有使用者訊息，沒有會在api的資料庫建立使用者資料。
3. 使用者名稱以及token等相關資訊會夾帶在response的COOKIE當中。

## 購物車全體操作:

1. GET method:
    * url pattern: http(s)://domain/api/cart
    * response:
   ```
    [
        {
            "id": 主鍵編號,
            "product": {  
                "id": 產品主鍵編號,
                "product_id": 產品編號,
                "product_name": 產品名稱,
                "price": 價格,
                "sale_price": 特價價格,
                "inventory": 存貨數,
                "class_name": table名稱,
                "app_name": app/db名稱,
            },
            "user": 使用者編號,
            "quantity": 購物車數量,
            "valid": 是否有效,
            "total_price": 選取數量的總價格,
        },
        ...
    ]
    ```
2. POST method:
   * url pattern: http(s)://domain/api/cart/
   
   * parameter:
     ```
     { 
         "product_id": 產品編號,
         "product_name": 產品名稱,
         "price": 價格,
         "sale_price": 特價價格, [選填]
         "inventory": 存貨數,
         "class_name": table名稱,
         "app_name": app/db名稱,
         "quantity": 購物車數量,
         "valid": 是否有效,
     }
     ```
   * 如果產品內部已經含有相同編號、table名稱、app/db名稱的產品資料，則不會新創見一筆產品資料，也不會更新產品資料於其中，返回的結果是資料庫已儲存的舊資料。
   * response:
      ```
       {
           "id": 主鍵編號,
           "product": {  
               "id": 產品主鍵編號,
               "product_id": 產品編號,
               "product_name": 產品名稱,
               "price": 價格,
               "sale_price": 特價價格,
               "inventory": 存貨數,
               "class_name": table名稱,
               "app_name": app/db名稱,
           },
           "user": 使用者編號,
           "quantity": 購物車數量,
           "valid": 是否有效,
           "total_price": 選取數量的總價格,
       },
     ```


## 購物車單一條目操作:

1. GET method:
    * url pattern: http(s)://domain/api/cart/cart_id(主鍵編號)
    * response:
   ```
    {
        "id": 主鍵編號,
        "product": {  
            "id": 產品主鍵編號,
            "product_id": 產品編號,
            "product_name": 產品名稱,
            "price": 價格,
            "sale_price": 特價價格,
            "inventory": 存貨數,
            "class_name": table名稱,
            "app_name": app/db名稱,
        },
        "user": 使用者編號,
        "quantity": 購物車數量,
        "valid": 是否有效,
        "total_price": 選取數量的總價格,
    }
   ```

2. PUT method:
   * url pattern: http(s)://domain/api/cart/cart_id(主鍵編號)
   * parameter:
     ```
     { 
           "quantity": 購物車數量,
           "valid": 是否有效,
     }
     ```
   * 可以更新購物車中欲購買項目的數量，以及是否有效。
   * response:
      ```
       {
           "id": 主鍵編號,
           "product": {  
               "id": 產品主鍵編號,
               "product_id": 產品編號,
               "product_name": 產品名稱,
               "price": 價格,
               "sale_price": 特價價格,
               "inventory": 存貨數,
               "class_name": table名稱,
               "app_name": app/db名稱,
           },
           "user": 使用者編號,
           "quantity": 購物車數量,
           "valid": 是否有效,
           "total_price": 選取數量的總價格,
       },
     ```
3. DELETE method:
   * url pattern: http(s)://domain/api/cart/cart_id(主鍵編號)
   * response:
     ```
       {
           "message": 顯示已刪除購物車欄目的編號(id)
       }
     ```


## 購物車單一條目操作:

1. GET method:
    * url pattern: http(s)://domain/api/cart/product/product_id(產品編號)/class_name(table名稱)/app_name(app/db名稱)
    * response:
   ```
   {  
       "id": 產品主鍵編號,
       "product_id": 產品編號,
       "product_name": 產品名稱,
       "price": 價格,
       "sale_price": 特價價格,
       "inventory": 存貨數,
       "class_name": table名稱,
       "app_name": app/db名稱,
   }
   ```

2. POST method:
   * url pattern: http(s)://domain/api/cart/product/product_id(產品編號)/class_name(table名稱)/app_name(app/db名稱)
   * parameter:
     ```
     { 
         "product_name": 產品名稱,
         "price": 價格,
         "sale_price": 特價價格, [選填]
         "inventory": 存貨數,
     }
     ```
   * parameter為新增產品資訊時所需要的必要資料。
   * response:
      ```
       {
           "id": 產品主鍵編號,
           "product_id": 產品編號,
           "product_name": 產品名稱,
           "price": 價格,
           "sale_price": 特價價格,
           "inventory": 存貨數,
           "class_name": table名稱,
           "app_name": app/db名稱,
       },
     ```
     
3. PUT method:
   * url pattern: http(s)://domain/api/cart/product/product_id(產品編號)/class_name(table名稱)/app_name(app/db名稱)
   * parameter:
     ```
     { 
         "product_name": 產品名稱,
         "price": 價格,
         "sale_price": 特價價格, [選填]
         "inventory": 存貨數,
     }
     ```
   * parameter為可以變更的資料。
   * response:
      ```
       {
           "id": 產品主鍵編號,
           "product_id": 產品編號,
           "product_name": 產品名稱,
           "price": 價格,
           "sale_price": 特價價格,
           "inventory": 存貨數,
           "class_name": table名稱,
           "app_name": app/db名稱,
       },
4. DELETE method:
   * url pattern: http(s)://domain/api/cart/product/product_id(產品編號)/class_name(table名稱)/app_name(app/db名稱)
   * response:
     ```
       {
           "message": 顯示產品已刪除
       }
     ```

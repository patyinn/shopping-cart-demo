from functools import wraps

from django.http import HttpResponse, JsonResponse
from django.views import View
from django.views.decorators.http import require_http_methods
from django.db.models import Q

from plant_app.models import ChildPlantModel

CART_ID = "CART_555"

# Create your views here.
class CartView(View):

    def __process_data(func):
        @wraps(func)
        def wrap(request, *args, **kwargs):
            s, m, c = func(request, *args, **kwargs)
            content = {
                "success": s,
                "message": m,
                "content": c,
            }
            return HttpResponse(JsonResponse(content))
        return wrap

    @classmethod
    @__process_data
    def read_cart(cls, request):
        cart_obj = request.session.get(CART_ID)
        if not cart_obj:
            cart_obj = {
                "cart_items": [],
                "cart_price": 0,
                "cart_amount": 0,
            }

        return (
            True,
            "get cart content successfully",
            cart_obj,
        )


    @classmethod
    @require_http_methods(["POST"])
    @__process_data
    def update_cart(cls, request):
        cart_obj = request.session.get(CART_ID)
        if not cart_obj:
            return (
                False,
                "No cart object",
                "",
            )

        ids = request.POST.getlist("merchandise_id")
        qtys = request.POST.getlist("qty")

        session_idxs = {obj["id"]: i for i, obj in enumerate(cart_obj["cart_items"])}
        diff_price = 0
        for id, qty in zip(ids, qtys):
            idx = session_idxs[id]
            cart_item = request.session[CART_ID]["cart_items"][idx]
            price = cart_item["sale_price"] if cart_item["sale_price"] else cart_item["price"]
            new_price = price * int(qty)
            diff_price += new_price - cart_item["total_price"]
            cart_item.update({
                "qty": qty,
                "total_price": new_price,
            })

        request.session[CART_ID]["total_price"] += diff_price
        request.session[CART_ID]["cart_amount"] = len(request.session[CART_ID]["cart_items"])
        request.session.modified = True

        return (
            True,
            "update cart successfully",
            cart_obj,
        )



    @classmethod
    @require_http_methods(["POST"])
    @__process_data
    def add_cart(cls, request):
        cart_obj = request.session.get(CART_ID)

        id = request.POST.get("merchandise_id")
        qty = request.POST.get("qty")
        cart_values = ChildPlantModel.objects\
            .filter(Q(id=id) & Q(status=ChildPlantModel.Status.ITINERARY)).values()

        if cart_values:
            cart_value = cart_values[0]
            qty = qty if cart_value["inventory"] >= qty else cart_value["inventory"]
            cart_value["qty"] = qty
            price = cart_value["sale_price"] if cart_value["sale_price"] else cart_value["price"]
            cart_value["total_price"] = int(cart_value["qty"]) * price

            if not cart_obj:
                request.session[CART_ID] = {
                    "cart_items": [cart_value],
                    "cart_price": cart_value["total_price"],
                    "cart_amount": 1,
                }
            else:
                request.session[CART_ID]["cart_items"].append(cart_value)
                request.session[CART_ID]["cart_amount"] = len(request.session[CART_ID]["cart_items"])
                request.session[CART_ID]["total_price"] += cart_value["total_price"]

            request.session.modified = True

            return (
                True,
                "append {}, qty: {} into cart".format(cart_value["name"], qty),
                "",
            )
        else:
            return (
                False,
                "missing product in db!",
                "",
            )


    @classmethod
    @require_http_methods(["POST"])
    @__process_data
    def remove_cart(cls, request):
        cart_obj = request.session.get(CART_ID)
        if not cart_obj:
            return (
                False,
                "No cart object",
                "",
            )

        id = request.POST.get("merchandise_id")


        session_idxs = [i for i, obj in enumerate(cart_obj["cart_items"]) if obj["id"] == id]
        session_idxs.sort(reverse=True)

        if session_idxs:
            diff_price = 0
            for ss_idx in session_idxs:
                cart_item = request.session[CART_ID]["cart_items"][ss_idx]
                name = cart_item["name"]
                diff_price += cart_item["total_price"]
                del cart_item

            request.session[CART_ID]["total_price"] -= diff_price
            request.session[CART_ID]["cart_amount"] = len(request.session[CART_ID]["cart_items"])
            request.session.modified = True

            return (
                True,
                "remove {} from cart".format(name),
                cart_obj,
            )

        else:
            return (
                False,
                "this item is not in the cart",
                cart_obj,
            )
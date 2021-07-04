from django.shortcuts import render, get_object_or_404, HttpResponse
from .models import PlantModel, CustomerModel
from .forms import CustomerModelForm
import datetime

# Create your views here.
def index(request):
    plant = PlantModel.objects
    return render(request, 'index.html', {'plant_object': plant})

def plant_page(request, id):

    plant_detail = get_object_or_404(PlantModel, pk=id)
    form = CustomerModelForm()
    if id:
        title = PlantModel.objects.get(id=id)
        price = plant_detail.price
        inv = int(plant_detail.inventory)
        inv_list = [i+1 for i in range(inv)]
        if 'purchase' in request.POST:
            form = CustomerModelForm(request.POST)
            if form.is_valid():
                customer = request.POST["customer"]
                email = request.POST["email"]
                add = request.POST["address"]
                tel = request.POST["tel"]
                qty = request.POST.get('qty')
                deal_date = datetime.datetime.now()
                inv -= int(qty)
                PlantModel.objects.filter(id=id).update(inventory=inv)
                CustomerModel.objects.create(
                    title=title,
                    price=price,
                    customer=customer,
                    tel=tel,
                    address=add,
                    qty=qty,
                    email=email,
                    deal_date=deal_date
                )
                return render(request, 'plants/complete_page.html', {'details': plant_detail})
    context = {
        'details': plant_detail,
        'inventory': inv_list,
        'form': form
    }
    return render(request, 'plants/detail.html', context)

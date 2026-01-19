from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Coupon

@login_required(login_url='/client/login/')
def create_order(request):
    return render(request, 'billing/create_order.html')



# @require_POST
def apply_coupon(request):
    code = request.POST.get("code", "").strip().upper()
    amount = request.POST.get("amount", "").strip()

    try:
        amount = int(amount)
    except:
        return JsonResponse({"success": False, "message": "Invalid amount!"})

    if not code:
        return JsonResponse({"success": False, "message": "Coupon code is required!"})

    try:
        coupon = Coupon.objects.get(code=code)
    except Coupon.DoesNotExist:
        return JsonResponse({"success": False, "message": "Invalid coupon!"})

    if not coupon.is_valid_now():
        return JsonResponse({"success": False, "message": "Coupon is expired or inactive!"})

    if amount < coupon.min_order_amount:
        return JsonResponse({
            "success": False,
            "message": f"Minimum order amount must be ₹{coupon.min_order_amount} for this coupon."
        })

    discount = 0

    if coupon.discount_type == "flat":
        discount = coupon.discount_value

    elif coupon.discount_type == "percent":
        discount = int((amount * coupon.discount_value) / 100)

    if discount > amount:
        discount = amount

    final_amount = amount - discount

    return JsonResponse({
        "success": True,
        "message": "Coupon applied successfully ✅",
        "discount": discount,
        "final_amount": final_amount,
        "coupon_code": coupon.code,
        "discount_type": coupon.discount_type,
        "discount_value": coupon.discount_value
    })

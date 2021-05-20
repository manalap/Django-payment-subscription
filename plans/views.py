from django.shortcuts import render, get_object_or_404, redirect
from .forms import CustomSignupForm
from django.urls import reverse_lazy
from django.views import generic
from .models import MiningPlan, Customer
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
import stripe
from django.http import HttpResponse

stripe.api_key = "sk_live_t3f5L4dT08nrLmyNbWXUCzCQ"


def home(request):
    plans = MiningPlan.objects
    return render(request, 'plans/join.html', {'plans': plans})


def plan(request, pk):
    plan = get_object_or_404(MiningPlan, pk=pk)
    if plan.premium:
        if request.user.is_authenticated:
            try:
                if request.user.customer.membership:
                    return render(request, 'plans/plan.html', {'plan': plan})
            except Customer.DoesNotExist:
                return redirect('join')
        return redirect('join')
    else:
        return render(request, 'plans/plan.html', {'plan': plan})


def join(request):
    return render(request, 'plans/join.html')


@login_required
def checkout(request):

    try:
        if request.user.customer.membership:
            return redirect('settings')
    except Customer.DoesNotExist:
        pass

    coupons = {'bademjun': 31, 'karafs': 10}
    amount = 0.00
    if request.method == 'POST':
        stripe_customer = stripe.Customer.create(
            email=request.user.email, source=request.POST['stripeToken'])
        if request.POST['plan'] == 'daily':
            plan = 'price_1IqDZbC5S6Zh0s4mjKDqwCMq'
            amount = 1000
            
        if request.POST['plan'] == 'weekly':
            plan = 'price_1Iq018C5S6Zh0s4mWgREHOq5'
            amount = 10000
        if request.POST['plan'] == 'monthly':
            plan = 'price_1Iq02nC5S6Zh0s4m4xee4hFX'
            amount = 30000
        if request.POST['coupon'] in coupons:
            percentage = coupons[request.POST['coupon'].lower()]
            try:
                coupon = stripe.Coupon.create(duration='once', id=request.POST['coupon'].lower(),
                                              percent_off=percentage)
            except:
                pass
            subscription = stripe.Subscription.create(customer=stripe_customer.id,
                                                      items=[{'plan': plan}], coupon=request.POST['coupon'].lower())
        else:
            subscription = stripe.Subscription.create(customer=stripe_customer.id,
                                                      items=[{'plan': plan}])

        customer = Customer()
        customer.user = request.user
        customer.stripeid = stripe_customer.id
        customer.membership = True
        customer.cancel_at_period_end = False
        customer.user_balance = amount
        customer.stripe_subscription_id = subscription.id
        customer.save()

        return redirect('home')
    else:
        coupon = 'none'
        plan = 'daily'
        price = 100000
        og_dollar = 1000
        coupon_dollar = 0
        final_dollar = 1000
        if request.method == 'GET' and 'plan' in request.GET:
            if request.GET['plan'] == 'weekly':
                plan = 'weekly'
                price = 1000000
                og_dollar = 10000
                final_dollar = 10000
        if request.method == 'GET' and 'plan' in request.GET:
            if request.GET['plan'] == 'monthly':
                plan = 'monthly'
                price = 3000000
                og_dollar = 30000
                final_dollar = 30000
        if request.method == 'GET' and 'coupon' in request.GET:
            print(coupons)
            if request.GET['coupon'].lower() in coupons:
                print('fam')
                coupon = request.GET['coupon'].lower()
                percentage = coupons[request.GET['coupon'].lower()]

                coupon_price = int((percentage / 100) * price)
                price = price - coupon_price
                coupon_dollar = str(coupon_price)[
                    :-2] + '.' + str(coupon_price)[-2:]
                final_dollar = str(price)[:-2] + '.' + str(price)[-2:]

        return render(request, 'plans/checkout.html',
                      {'plan': plan, 'coupon': coupon, 'price': price, 'og_dollar': og_dollar,
                       'coupon_dollar': coupon_dollar, 'final_dollar': final_dollar, 'amount': amount})

@login_required
def settings(request):
    balance = 0.00
    membership = False
    cancel_at_period_end = False
    if request.method == 'POST':
        subscription = stripe.Subscription.retrieve(
            request.user.customer.stripe_subscription_id)
        subscription.cancel_at_period_end = True
        request.user.customer.cancel_at_period_end = True
        cancel_at_period_end = True
        subscription.save()
        request.user.customer.save()
    else:
        try:
            if request.user.customer.membership:
                membership = True
                balance = request.user.customer.user_balance
            if request.user.customer.cancel_at_period_end:
                cancel_at_period_end = True
        except Customer.DoesNotExist:
            membership = False
            balance = 0.00
    return render(request, 'registration/settings.html', {'membership': membership,
                                                          'cancel_at_period_end': cancel_at_period_end,
                                                          'balance': balance})


@user_passes_test(lambda u: u.is_superuser)
def updateaccounts(request):
    customers = Customer.objects.all()
    for customer in customers:
        subscription = stripe.Subscription.retrieve(
            customer.stripe_subscription_id)
        if subscription.status != 'active':
            customer.membership = False
        else:
            customer.membership = True
        customer.cancel_at_period_end = subscription.cancel_at_period_end
        customer.save()
    return HttpResponse('completed')


class SignUp(generic.CreateView):
    form_class = CustomSignupForm
    success_url = reverse_lazy('home')
    template_name = 'registration/signup.html'

    def form_valid(self, form):
        valid = super(SignUp, self).form_valid(form)
        username, password = form.cleaned_data.get(
            'username'), form.cleaned_data.get('password1')
        new_user = authenticate(username=username, password=password)
        login(self.request, new_user)
        return valid



def betting(request):
    balance = 0.00
    try:
        if request.user.customer:
            balance = user.customer.user_balance
    except Customer.DoesNotExist:
            balance = 0.00
                
    return render(request, 'plans/betting.html', {'balance': balance})


    
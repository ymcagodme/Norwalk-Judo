import hashlib

class Login_record(models.Model):
    account = models.ForeignKey()
    date = models.DateTimeField(auto_now=True)
    ip_addr = models.IPAddressField()
    successfully_login = models.BooleanField()
    
class Account(models):
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=100)
    permission_level = models.PositiveIntegerField()
    last_login = models.DateTimeField()

def custom_login(request):
    #FIXME read the next page parameter. use a hidden field to pass the uri
    if request.session.get('username'):
        return HttpResponse('Already Login')
    if request.method == 'POST':
        user = account.objects.get(username=request.POST.get('username')
        password = request.POST.get('password')
        password = hashlib.sha512(password).hexdigest()
        try:
            ip_addr = request.META['REMOTE_ADDR']
            if password is user.password:
                request.session['username'] = username
                record = Login_record.create(account=user, ip_addr=ip_addr, successfully_login=True)
                record.save()
                return HttpResponse('Successfully login')
            else:
                record = Login_record.create(account=user, ip_addr=ip_addr, successfully_login=False)
                record.save()
                return HttpResponse('Wrong Password')
        except AttributeError:
            return HttpResponse('Invalid Username')
    return render_to_response('custom_login.html')

def custom_logout(request):
    try:
        del request.session['username']
    except KeyError:
        pass
    return HttpResponse('You\'re logged out')

# This is a decorator
class president_login_required(object):
    def __init__(self, f):
        self.f = f
    def __call__(self, request):
        if request.session.get('username') is None:
            #FIXME need HttpRedirect() 
            return HttpRedirect('Login Page')
        #FIXME consider the next page situation
        self.f(request)


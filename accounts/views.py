from django.shortcuts import render,redirect
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib import messages
from .forms import SignupForm,SeekerAccountForm,RecruiterAccountForm
from .models import User, Seeker, Recruiter
from django.db.models.signals import post_save,post_delete
from django.core.exceptions import ValidationError
from email_validator import validate_email
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from .tokens import account_activation_token
# Create your views here.

def accounts(request):
    return render(request, 'accounts/accountsHome.html')

def main(request):
    return render(request, 'main.html')

def SignUpType(request):
	return render(request,'signup_login.html')

def userProfile(request):
	return render(request,'profile.html')

def userLogout(request):
    logout(request)
    messages.info(request ,'User was logged out!')
    return redirect('login')

def Profile(request):
	return render(request,'signup_login.html')

def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.email_verified= True
        user.save()


        messages.success(request, "Thank you, your account is now activated. Try to login")
        return redirect('login-after-active')
    else:
        messages.error(request, "Activation link is invalid!")

    return redirect('login')

def activateEmail(request, user, to_email):
    mail_subject = "Activate your user account."
    message = render_to_string("template_activate_account.html", {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        "protocol": 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        messages.success(request, f'Dear {user}, please go to your email {to_email} inbox and click on \
                received activation link to confirm and complete the registration. \n Note: Check your spam folder.')
    else:
        messages.error(request, f'Problem sending email to {to_email}, check if you typed it correctly.')


def userSignUp(request):

    page = 'register'
    form = SignupForm()

    if request.method == 'POST':
        form = SignupForm(request.POST)
        email = request.POST.get('email')
        
        if form.is_valid():

         if not validate_email(email):
                 messages.error(request,
                                 'Enter a valid email address')
         else:
                 
            user = form.save(commit=False)
            user.email = user.email.lower()
            #user.email_verified = True
            UserType= request.POST.get('User_Type')
            

            if(UserType=='Seeker'):
               user.is_Seeker= True
            else:
                user.is_Recruiter = True

            user.save()
            
            if(UserType=='Seeker'):
               seeker = Seeker.objects.create(user=user,
                                              username=user.username,
                                              email=user.email,
                                              name=user.first_name,
                                              )
            else:
                recruiter = Recruiter.objects.create(user=user,
                                                     username=user.username,
                                                     email=user.email,
                                                     name=user.first_name,)

            activateEmail(request, user, form.cleaned_data.get('email'))
            return redirect('login')
            # messages.success(request, 'User account was created!')

            #login(request, user)
            #return redirect('edit-account')

        else:
            messages.error(
                request, 'An error has occurred during registration')
        


    context = {'page': page, 'form': form}
    return render(request, 'signup_login.html', context)

def userLogin(request):

    page = 'login'
    
    if request.user.is_authenticated:
       return redirect('main')

    if request.method == 'POST':
        email = request.POST['email'].lower()
        password = request.POST['password']

        try:
            user = User.objects.get(email=email)
        except:

            messages.error(request, 'Email does not exist')
            return redirect('login')

        user = authenticate(request, email=email, password=password)

        user2 = User.objects.get(email=email)
        if user2.email_verified:
            if user is not None:
                login(request, user)#create session
                return redirect('account')

            else:
                messages.error(request, 'Email OR password is incorrect')
        else:
            messages.error(request, 'check your email inbox to activate your account')

    return render(request, 'signup_login.html')


@login_required(login_url='login')
def userAccount(request):

    if request.user.is_Seeker:
       account=request.user.seeker
       skills = account.skill_set.all()
    if request.user.is_Recruiter:
        account=request.user.recruiter
    
    
   
    context = {'account': account}
    return render(request, 'account.html', context)

def userLoginActivate(request):

    
    page = 'login'
    
    if request.user.is_authenticated:
       return redirect('main')

    if request.method == 'POST':
        email = request.POST['email'].lower()
        password = request.POST['password']

        try:
            user = User.objects.get(email=email)
        except:

            messages.error(request, 'Email does not exist')
            return redirect('login')

        user = authenticate(request, email=email, password=password)

        user2 = User.objects.get(email=email)
        if user2.email_verified:
            if user is not None:
                login(request, user)#create session
                return redirect('edit-account')

            else:
                messages.error(request, 'Email OR password is incorrect')
        else:
            messages.error(request, 'check your email inbox to activate your account')

    return render(request, 'signup_login.html')

@login_required(login_url='login')
def editAccount(request):

    
    if request.user.is_Seeker:
        seeker = request.user.seeker
        form = SeekerAccountForm(instance=seeker)

    elif request.user.is_Recruiter:
        recruiter = request.user.recruiter
        form = RecruiterAccountForm(instance=recruiter)
        
    if request.method == 'POST':
            
        if request.user.is_Seeker:
             form = SeekerAccountForm(request.POST, request.FILES, instance=seeker)
             
             if form.is_valid():
                # Validate file extension
                file = form.cleaned_data.get('cv')
                try:
                    validate_word_or_text_file(file)
                except ValidationError as e:
                    form.add_error('cv', e)
                    messages.error(request, 'the cv format is not accepted, Try (.docx , .txt , .rtf)')
                    return render(request, 'account-edit.html', {'form': form})

                form.save()
                messages.success(request, 'Account has been updated')
                return redirect('account')     

        elif request.user.is_Recruiter:
            form = RecruiterAccountForm(request.POST, request.FILES, instance=recruiter)
            
            if form.is_valid():
                form.save()
                messages.success(request, 'Account has been updated')
                return redirect('account')
       

    context = {'form': form}
    return render(request, 'account-edit.html', context)

def validate_word_or_text_file(file):
    ext = file.name.split('.')[-1]
    if ext not in ['docx', 'txt', 'rtf']:
        raise ValidationError(f'File type "{ext}" is not supported.')



def updateUser(created,sender,instance,**kwargs):
    SeekerOrProvider=instance
    user=SeekerOrProvider.user
    if created == False:
        user.first_name = SeekerOrProvider.name
        user.username = SeekerOrProvider.username
        user.email = SeekerOrProvider.email
        user.is_active = SeekerOrProvider.is_active
        user.save()

post_save.connect(updateUser,sender=Seeker)
post_save.connect(updateUser,sender=Recruiter)



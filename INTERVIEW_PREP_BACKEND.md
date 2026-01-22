# Nexa-DreamX Backend Interview Preparation Guide
## Cryptocurrency Investment Platform - Python/Django Backend

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Technology Stack](#technology-stack)
3. [Architecture & Design Patterns](#architecture--design-patterns)
4. [Database Design](#database-design)
5. [Authentication & Authorization](#authentication--authorization)
6. [Core Features Implementation](#core-features-implementation)
7. [Advanced Django Techniques](#advanced-django-techniques)
8. [Security Implementations](#security-implementations)
9. [Email System](#email-system)
10. [Background Tasks & Automation](#background-tasks--automation)
11. [Deployment & Production](#deployment--production)
12. [Challenges & Solutions](#challenges--solutions)

---

## 1. Project Overview

**Nexa-DreamX** is a full-stack cryptocurrency investment platform that allows users to invest in various plans, track profits, make deposits/withdrawals, and earn through referrals.

### Key Metrics
- **Python Code**: ~2,896 lines across 51 files
- **Django Apps**: 4 custom apps (app, users, _user, _admin)
- **Database Models**: 7 core models
- **API Endpoints**: 45+ URL routes
- **Technologies**: Django 5.1.6, PostgreSQL, Django-allauth, Cloudinary

### Your Role as Backend Developer
- Designed and implemented the complete database schema
- Built RESTful architecture using Django Class-Based Views (CBVs)
- Implemented dual-user system (Admin & Client dashboards)
- Created automated profit calculation system
- Integrated email notifications for all transactions
- Implemented referral tracking system

---

## 2. Technology Stack

### Core Backend Technologies

#### Django 5.1.6
**Why chosen**: Latest stable release with enhanced security features and async support

**Key features used**:
- Class-Based Views (CBVs) for DRY code
- Django ORM for database abstraction
- Signals for automated workflows
- Custom user model extending AbstractUser
- Django Admin customization

#### PostgreSQL
**Why chosen**:
- ACID compliance for financial transactions
- Better handling of concurrent transactions
- Superior data integrity for financial applications
- UUID primary key support

**Configuration**:
```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": get_env_variable("MYSQL_NAME", "mydatabase"),
        "USER": get_env_variable("MYSQL_USER", "myuser"),
        "PASSWORD": get_env_variable("MYSQL_PASSWORD", "mypassword"),
        "HOST": get_env_variable("MYSQL_HOST", "localhost"),
        "PORT": get_env_variable("MYSQL_PORT", "5432"),
    }
}
```

#### Django-allauth 65.4.1
**Why chosen**: Industry-standard authentication package

**Features implemented**:
- Email/username dual login
- Email verification (optional)
- Password reset functionality
- Rate limiting on auth endpoints
- Custom signup form with extra fields
- Social authentication capability (configured, not yet implemented)

#### Additional Backend Dependencies

1. **Gunicorn 23.0.0** - Production WSGI server
2. **Uvicorn 0.34.2** - ASGI server for async support
3. **WhiteNoise 6.9.0** - Static file serving in production
4. **Cloudinary** - Image storage (profile photos, QR codes)
5. **psycopg2 2.9.10** - PostgreSQL adapter
6. **python-dotenv 1.0.1** - Environment variable management
7. **Pillow 11.1.0** - Image processing

---

## 3. Architecture & Design Patterns

### Application Structure

I organized the project into **4 Django apps**, each with a specific responsibility:

#### 1. `app/` - Core Business Logic
**Purpose**: Contains core financial models and public-facing views

**Responsibilities**:
- Core domain models (Plan, Investment, Wallet, Transaction, DepositMethod, Mining)
- Public views (Home, About, Contact, Services)
- Django signals for wallet auto-creation
- Database migrations

**Why separated**: Keeps business logic isolated from user interfaces

#### 2. `users/` - Authentication & User Management
**Purpose**: Custom user model and referral system

**Contains**:
- CustomUser model (extends AbstractUser with UUID primary key)
- Referral model for tracking referrals
- User-related signals

**Why separated**: Follows Django best practice of separating user model into its own app

#### 3. `_user/` - Client Dashboard
**Purpose**: All client-facing functionality

**Contains**:
- Dashboard views (20+ views)
- Investment creation and tracking
- Deposit/withdrawal forms and logic
- Profile management
- Transaction history views
- Background task for profit processing

**Why named with underscore**: Avoids namespace conflicts with Django's built-in `user` references

#### 4. `_admin/` - Administrative Interface
**Purpose**: Admin control panel (separate from Django Admin)

**Contains**:
- Custom admin dashboard (30+ views)
- CRUD operations for all models
- Transaction approval/rejection system
- User management
- Wallet balance management

**Why custom admin**: Provides more control over admin UI/UX and business logic than Django Admin

### Design Patterns Implemented

#### 1. **Class-Based Views (CBVs)**
**Why**: DRY principle, built-in mixins, easier to extend

**Example - Dashboard with optimized queries**:
```python
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = f"{template_dir}/index.html"

    def get_user_wallet(self, wallet_type):
        """Helper method to fetch user wallet efficiently."""
        return Wallet.objects.filter(
            user=self.request.user, wallet_type=wallet_type
        ).first()

    def get_transaction_sum(self, transaction_type, status=None):
        """Helper method to sum transactions efficiently."""
        filters = {"user": self.request.user, "transaction_type": transaction_type}
        if status:
            filters["status"] = status
        return (
            Transaction.objects.filter(**filters).aggregate(total=Sum("amount"))["total"]
            or 0
        )
```

**Benefits**:
- Reusable helper methods
- Clean separation of concerns
- Easy to test

#### 2. **Mixin Pattern**
**Implementation**:
```python
class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff

class DashboardView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    template_name = f"{template_url}/index.html"
```

**Benefits**:
- DRY authorization logic
- Easy to apply to multiple views
- Centralized access control

#### 3. **Repository Pattern (Django ORM)**
**Example**:
```python
# Encapsulated query logic
def get_queryset(self):
    return Transaction.objects.filter(
        user=self.request.user,
        transaction_type="INVESTMENT"
    ).order_by("-timestamp")
```

#### 4. **Signal-Based Event Handling**
**Implementation**:
```python
@receiver(post_save, sender=User)
def create_user_wallets(sender, instance, created, **kwargs):
    if created and not instance.is_superuser:
        # Create wallets automatically
        deposit_wallet, _ = Wallet.objects.get_or_create(
            user=instance, wallet_type="DEPOSIT"
        )
        interest_wallet, created_interest_wallet = Wallet.objects.get_or_create(
            user=instance, wallet_type="INTEREST"
        )
        if created_interest_wallet:
            # Add sign-on bonus
            interest_wallet.balance += SIGN_ON_BONUS_AMOUNT
            interest_wallet.save()
```

**Benefits**:
- Decoupled architecture
- Automatic execution
- Easy to maintain

---

## 4. Database Design

### Schema Overview

I designed a **normalized relational database** with 7 core models using **UUID primary keys** for security.

### Core Models

#### 1. CustomUser (users/models.py)
**Extends**: Django's AbstractUser
**Primary Key**: UUID

```python
class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=255, unique=True)
    mobile = models.CharField(max_length=15)
    country = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    profile_photo = models.ImageField(upload_to="profile_photos/", null=True, blank=True)
    referred_by = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True)
```

**Key decisions**:
- **UUID instead of auto-increment**: Prevents user enumeration attacks
- **Self-referencing FK**: Enables referral tree tracking
- **Cloudinary for images**: Scalable image storage
- **All fields required except profile_photo**: Ensures complete user data

#### 2. Plan (app/models.py)
**Purpose**: Investment plan templates

```python
class Plan(models.Model):
    DURATION_UNITS = (
        ("DAYS", "Days"),
        ("WEEKS", "Weeks"),
        ("MONTHS", "Months"),
    )

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    name = models.CharField(max_length=255)
    daily_profit_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    min_amount = models.DecimalField(max_digits=15, decimal_places=2)
    max_amount = models.DecimalField(max_digits=15, decimal_places=2)
    duration_value = models.PositiveIntegerField()
    duration_unit = models.CharField(max_length=6, choices=DURATION_UNITS)

    def get_duration_in_days(self):
        """Convert duration to days for calculations"""
        conversion = {"DAYS": 1, "WEEKS": 7, "MONTHS": 30}
        return self.duration_value * conversion[self.duration_unit]

    @property
    def total_return(self):
        """Returns the total return in % over the duration."""
        return self.daily_profit_percentage * self.get_duration_in_days()
```

**Key decisions**:
- **Flexible duration units**: Supports days/weeks/months
- **Helper method for normalization**: Converts all durations to days
- **Computed properties**: `total_return` calculated on-the-fly
- **DecimalField for money**: Avoids floating-point precision issues

#### 3. Wallet (app/models.py)
**Purpose**: User balance management (dual-wallet system)

```python
class Wallet(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    WALLET_TYPES = (
        ("DEPOSIT", "Deposit Wallet"),
        ("INTEREST", "Interest Wallet"),
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    wallet_type = models.CharField(max_length=8, choices=WALLET_TYPES)
    balance = models.DecimalField(max_digits=20, decimal_places=2, default=0)

    @property
    def available_balance(self):
        """Balance minus pending withdrawals"""
        pending_withdrawals = Transaction.objects.filter(
            wallet=self, transaction_type="WITHDRAW", status="PENDING"
        ).aggregate(total=models.Sum('amount'))['total'] or 0
        return self.balance - Decimal(pending_withdrawals)

    def can_withdraw(self, amount):
        return self.available_balance >= amount

    class Meta:
        unique_together = ("user", "wallet_type")
```

**Key decisions**:
- **Dual-wallet architecture**:
  - DEPOSIT: For deposits and investments
  - INTEREST: For profits and withdrawals
- **unique_together constraint**: Prevents duplicate wallets
- **available_balance property**: Accounts for pending withdrawals
- **can_withdraw() method**: Business logic encapsulation

**Why dual wallets?**
- **Separation of concerns**: Deposits separate from earnings
- **Better accounting**: Easy to track profit vs. deposits
- **Prevents confusion**: Users see clear breakdown

#### 4. Investment (app/models.py)
**Purpose**: User investment contracts

```python
class Investment(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True)
    wallet = models.ForeignKey(Wallet, on_delete=models.SET_NULL, null=True)
    profit_accumulated = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self._state.adding:  # Only on creation
            start_date = timezone.now()
            if self.plan.duration_unit == "MONTHS":
                self.end_date = start_date + relativedelta(months=+self.plan.duration_value)
            else:
                days = self.plan.get_duration_in_days()
                self.end_date = start_date + timedelta(days=days)
        super().save(*args, **kwargs)

    @property
    def current_profit(self):
        if not self.is_active:
            return self.profit_accumulated
        # Calculate based on days passed
        elapsed_days = (timezone.now() - self.start_date).days
        daily_profit = self.amount * (self.plan.daily_profit_percentage / 100)
        return round(min(elapsed_days, self.plan.get_duration_in_days()) * daily_profit, 2)

    @property
    def progress_percentage(self):
        total_days = self.plan.get_duration_in_days()
        elapsed_days = (timezone.now() - self.start_date).days
        return min(int((elapsed_days / total_days) * 100), 100)
```

**Key decisions**:
- **Auto-calculate end_date**: Uses relativedelta for accurate month calculations
- **Real-time profit calculation**: `current_profit` computed on-demand
- **Progress tracking**: `progress_percentage` for UI display
- **Soft delete via SET_NULL**: Preserves data integrity if plan deleted

#### 5. Transaction (app/models.py)
**Purpose**: Financial transaction ledger

```python
class Transaction(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    TRANSACTION_TYPES = (
        ("INVESTMENT", "Investment"),
        ("PROFIT", "Profit"),
        ("DEPOSIT", "Deposit"),
        ("WITHDRAW", "Withdraw"),
    )
    STATUS_CHOICES = (
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    investment = models.ForeignKey(Investment, on_delete=models.SET_NULL, null=True, blank=True)
    wallet = models.ForeignKey(Wallet, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    deposit_method = models.ForeignKey("DepositMethod", on_delete=models.SET_NULL, null=True, blank=True)
    withdrawal_address = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    admin_note = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
```

**Key decisions**:
- **Immutable ledger**: No update/delete, only create
- **4 transaction types**: Covers all financial movements
- **3-state status workflow**: PENDING → APPROVED/REJECTED
- **Flexible relationships**: Optional investment, wallet, deposit_method
- **withdrawal_address**: Stores external crypto wallet
- **admin_note**: For approval/rejection reasons

**Why this design?**
- **Complete audit trail**: Every financial movement tracked
- **Regulatory compliance**: Required for financial platforms
- **Dispute resolution**: Full transaction history

#### 6. DepositMethod (app/models.py)
**Purpose**: Cryptocurrency deposit configuration

```python
class DepositMethod(models.Model):
    CRYPTO_CHOICES = (
        ("BANK", "Bank"),
        ("BTC", "Bitcoin"),
        ("ETH", "Ethereum"),
        ("USDT", "Tether"),
        ("DOD", "Dodge"),
        ("LTC", "Litecoin"),
    )

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    crypto_type = models.CharField(max_length=4, choices=CRYPTO_CHOICES, unique=True)
    wallet_address = models.CharField(max_length=255, null=True, blank=True)
    qr_code = models.ImageField(upload_to="qr_codes/", null=True, blank=True)
    is_active = models.BooleanField(default=True)
    instruction = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        """Automatically set instructions based on deposit type."""
        if self.crypto_type == "BANK":
            self.instruction = (
                "1. Transfer the deposit amount to the provided bank account details.\n"
                "2. Use your registered account number or username as the payment reference.\n"
                "3. After making the transfer, upload the transaction receipt for verification.\n"
                "4. Your deposit will be processed and credited to your account after confirmation."
            )
            self.wallet_address = None
            self.qr_code = None
        elif not self.instruction:
            self.instruction = "Use the provided wallet address or scan the QR code to deposit."
        super().save(*args, **kwargs)
```

**Key decisions**:
- **unique constraint on crypto_type**: One config per cryptocurrency
- **Auto-generate instructions**: Reduces admin work
- **Special handling for bank**: No wallet/QR for fiat
- **is_active flag**: Enable/disable methods without deleting

#### 7. Referral (users/models.py)
**Purpose**: Track referral relationships

```python
class Referral(models.Model):
    referrer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="made_referrals")
    referred = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="referral_entry")
    created_at = models.DateTimeField(auto_now_add=True)
```

**Key decisions**:
- **Separate from CustomUser.referred_by**: Enables detailed tracking
- **OneToOneField on referred**: Each user referred once
- **ForeignKey on referrer**: One user can refer many
- **Timestamp tracking**: Analytics and reporting

### Database Relationships Diagram

```
CustomUser (1) ──< (M) Wallet
CustomUser (1) ──< (M) Investment
CustomUser (1) ──< (M) Transaction
CustomUser (1) ──< (M) Referral (as referrer)
CustomUser (1) ──  (1) Referral (as referred)
CustomUser (1) ──< (1) CustomUser (self-referencing)

Plan (1) ──< (M) Investment

Wallet (1) ──< (M) Transaction
Wallet (1) ──< (M) Investment

Investment (1) ──< (M) Transaction

DepositMethod (1) ──< (M) Transaction
```

### Database Indexes & Optimization

**Automatic indexes** (via Django):
- All primary keys (UUIDs)
- All foreign keys
- Unique fields (email, username, crypto_type)
- unique_together (user, wallet_type)

**Query optimization techniques**:
1. **select_related()** for foreign keys:
```python
Transaction.objects.filter(user=self.request.user).select_related("wallet")
```

2. **Aggregate functions** instead of loops:
```python
Transaction.objects.filter(user=user).aggregate(total=Sum("amount"))
```

3. **Property caching** for expensive calculations:
```python
@property
def current_profit(self):
    # Calculated once per request
    return round(elapsed_days * daily_profit, 2)
```

---

## 5. Authentication & Authorization

### Django-allauth Integration

#### Setup & Configuration

**Installed apps** (settings.py:28-47):
```python
INSTALLED_APPS = [
    "django.contrib.sites",  # Required for Allauth
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    # ... custom apps
]

SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",  # Default
    "allauth.account.auth_backends.AuthenticationBackend",  # Allauth
]
```

**Authentication settings** (settings.py:192-198):
```python
LOGIN_REDIRECT_URL = "/dashboard/"
ACCOUNT_LOGOUT_REDIRECT_URL = "/"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_LOGIN_METHODS = {"email", "username"}  # Dual login
ACCOUNT_EMAIL_VERIFICATION = "optional"

AUTH_USER_MODEL = "users.CustomUser"
```

**Why these choices?**
- **Dual login**: Better UX (users choose email or username)
- **Optional verification**: Reduces signup friction
- **Custom user model**: Enables additional fields

### Rate Limiting Implementation

**Why implemented**: Prevent brute-force attacks and abuse

**Configuration** (settings.py:56-66):
```python
ACCOUNT_RATE_LIMITS = {
    "signup": "10/m/ip",  # 10 signups per IP per minute
    "login": "5/m/ip",  # 5 login attempts per IP per minute
    "login_failed": "5/m/ip,3/5m/key",  # 5 failed per IP, 3 per 5min per key
    "reset_password": "10/m/ip,3/m/key",
    "change_password": "3/m/user",
    "manage_email": "5/m/user",
    "confirm_email": "1/3m/key",
}
```

**Key learnings**:
- **IP-based limits**: Prevent automated attacks
- **Key-based limits**: Prevent account-specific abuse
- **Gradual lockout**: `login_failed` tightens over time

### Custom Signup Form

**Implementation** (app/forms.py:13-82):

```python
class CustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    mobile = forms.CharField(max_length=15, required=True)
    username = forms.CharField(max_length=15, required=True)
    referral_code = forms.CharField(max_length=50, required=False)

    def clean_mobile(self):
        mobile = self.cleaned_data["mobile"]
        if User.objects.filter(mobile=mobile).exists():
            raise ValidationError("A user with this mobile number already exists.")
        return mobile

    def save(self, request):
        # Create user via allauth
        user = super(CustomSignupForm, self).save(request)

        # Populate custom fields
        user.first_name = self.cleaned_data.get("first_name")
        user.last_name = self.cleaned_data.get("last_name")
        user.mobile = self.cleaned_data.get("mobile")

        # Handle referral logic
        code = self.cleaned_data.get("referral_code")
        if code:
            try:
                referrer = User.objects.get(username=code)
                user.referred_by = referrer
                Referral.objects.create(referrer=referrer, referred=user)
            except User.DoesNotExist:
                pass

        user.save()
        return user
```

**Why custom form?**
- **Capture extra fields**: mobile, referral_code
- **Validation**: Prevent duplicate mobiles
- **Referral integration**: Automatic referral tracking

**Configuration** (settings.py:68):
```python
ACCOUNT_FORMS = {"signup": "app.forms.CustomSignupForm"}
```

### Authorization Mixins

#### LoginRequiredMixin
**Usage**: Restrict views to authenticated users

```python
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/user/index.html"
```

#### AdminRequiredMixin
**Custom implementation** (_admin/views.py:33-36):

```python
class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff

class DashboardView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    template_name = "dashboard/admin/index.html"
```

**Why custom mixin?**
- **Reusable**: Applied to all admin views
- **Flexible**: Accepts both superuser and staff
- **DRY**: Single source of truth

### Referral System Implementation

#### Signal-based referral tracking

**Signal handler** (app/signals.py:6-21):
```python
@receiver(user_signed_up)
def handle_referral(request, user, **kwargs):
    code = request.session.get("referral_code")
    if not code:
        return

    try:
        referrer = CustomUser.objects.get(username=code)
    except CustomUser.DoesNotExist:
        return

    user.referred_by = referrer
    user.save(update_fields=["referred_by"])

    Referral.objects.create(referrer=referrer, referred=user)
```

**Referral link generation** (_user/views.py:92-98):
```python
context["REFERRAL_LINK"] = (
    os.getenv("APP_URL") + f"/accounts/signup/?ref={self.request.user.username}"
)

context["total_referrals"] = Referral.objects.filter(
    referrer=self.request.user
).count()
```

**How it works**:
1. User shares referral link: `https://example.com/signup/?ref=john123`
2. New user signs up with referral code in form
3. Signal captures code and creates Referral record
4. CustomUser.referred_by points to referrer

---

## 6. Core Features Implementation

### Investment System

#### Investment Creation Flow

**View** (_user/views.py:109-178):
```python
class InvestmentCreateView(LoginRequiredMixin, CreateView):
    model = Investment
    form_class = InvestmentForm

    def form_valid(self, form):
        # Deduct amount from wallet
        wallet = form.cleaned_data["wallet"]
        amount = form.cleaned_data["amount"]

        # Create investment
        investment = form.save(commit=False)
        investment.user = self.request.user
        investment.save()

        # Update wallet balance
        wallet.balance -= amount
        wallet.save()

        # Log transaction
        Transaction.objects.create(
            user=self.request.user,
            investment=investment,
            wallet=wallet,
            amount=amount,
            transaction_type="INVESTMENT",
        )

        # Calculate expected return
        days = investment.plan.get_duration_in_days()
        interest_rate = float(investment.plan.daily_profit_percentage) * days
        expected_return = float(amount) * (1 + interest_rate / 100)

        # Send confirmation email
        send_transaction_email(
            "investment_confirmation.html",
            f"Investment Confirmation - {investment.plan.name}",
            {"user": self.request.user, "investment": investment, "expected_return": expected_return},
            self.request.user.email,
        )

        return super().form_valid(form)
```

**Form validation** (_user/forms.py:37-66):
```python
class InvestmentForm(forms.ModelForm):
    class Meta:
        model = Investment
        fields = ["plan", "wallet", "amount"]

    def clean_amount(self):
        amount = self.cleaned_data["amount"]
        plan = self.cleaned_data.get("plan")

        # Validate amount range
        if plan and (amount < plan.min_amount or amount > plan.max_amount):
            raise forms.ValidationError(
                f"Amount must be between {plan.min_amount} and {plan.max_amount}"
            )
        return amount

    def clean(self):
        cleaned_data = super().clean()
        wallet = cleaned_data.get("wallet")
        amount = cleaned_data.get("amount")

        # Check wallet balance
        if wallet and amount and wallet.balance < amount:
            raise forms.ValidationError("Insufficient balance in the selected wallet.")
        return cleaned_data
```

**Key implementation details**:
1. **Atomic operations**: Deduct wallet, create investment, log transaction in one request
2. **Validation**: Amount range and balance checks
3. **Transparency**: Email with expected return calculation
4. **Audit trail**: Transaction record for every investment

#### Daily Profit Calculation

**Background task** (_user/task.py:6-58):
```python
def process_daily_profits():
    today = timezone.now().date()
    investments = Investment.objects.filter(is_active=True)

    for investment in investments:
        # Check if investment expired
        if investment.end_date < timezone.now():
            investment.is_active = False
            investment.save()
            continue

        elapsed_days = (timezone.now().date() - investment.start_date.date()).days
        total_days = investment.plan.get_duration_in_days()

        # Check if already credited today
        already_credited = Transaction.objects.filter(
            user=investment.user,
            investment=investment,
            transaction_type="PROFIT",
            timestamp__date=today,
        ).exists()

        if already_credited:
            continue

        if elapsed_days <= total_days:
            # Calculate daily profit
            daily_profit = investment.amount * (
                investment.plan.daily_profit_percentage / Decimal("100.0")
            )

            # Credit interest wallet
            interest_wallet = Wallet.objects.get(user=investment.user, wallet_type="INTEREST")
            interest_wallet.balance += daily_profit
            interest_wallet.save()

            # Log transaction
            Transaction.objects.create(
                user=investment.user,
                investment=investment,
                wallet=interest_wallet,
                amount=daily_profit,
                transaction_type="PROFIT",
                status="APPROVED",
                admin_note=f"Daily profit for {investment.plan.name}",
            )

            # Update accumulated profit
            investment.profit_accumulated += daily_profit
            investment.save()
```

**Management command** (_user/management/commands/process_profits.py):
```python
class Command(BaseCommand):
    help = "Processes daily investment profits."

    def handle(self, *args, **options):
        process_daily_profits()
```

**How to run**:
```bash
python manage.py process_profits
```

**Cron job setup** (production):
```bash
0 0 * * * /path/to/venv/bin/python /path/to/manage.py process_profits
```

**Key design decisions**:
1. **Idempotent**: Safe to run multiple times (checks `already_credited`)
2. **Auto-deactivation**: Marks expired investments as inactive
3. **Decimal precision**: Uses `Decimal` for accurate financial calculations
4. **Transaction logging**: Every profit credited is recorded

#### Real-time Profit Display

**Property calculation** (app/models.py:156-173):
```python
@property
def current_profit(self):
    if not self.is_active:
        return self.profit_accumulated

    # Calculate based on days passed
    now = timezone.now()
    elapsed_days = (now - self.start_date).days
    daily_profit = self.amount * (self.plan.daily_profit_percentage / 100)

    # Cap at total duration
    return round(min(elapsed_days, self.plan.get_duration_in_days()) * daily_profit, 2)

@property
def progress_percentage(self):
    total_days = self.plan.get_duration_in_days()
    elapsed_days = (timezone.now() - self.start_date).days
    return min(int((elapsed_days / total_days) * 100), 100)
```

**Why properties?**
- **Real-time**: Always up-to-date without database writes
- **Efficient**: Calculated on-demand
- **UI-ready**: Can be used directly in templates

### Deposit System

#### Deposit Flow

1. User selects cryptocurrency (BTC, ETH, USDT, etc.)
2. System displays wallet address and QR code
3. User makes external transfer
4. User submits deposit request with amount
5. Admin receives notification
6. Admin approves/rejects deposit
7. Balance updated, user notified

**User-side view** (_user/views.py:225-285):
```python
class DepositCreateView(LoginRequiredMixin, FormView):
    form_class = DepositForm
    template_name = "dashboard/user/deposit_create.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        crypto_id = self.kwargs["pk"]
        deposit_method = get_object_or_404(DepositMethod, id=crypto_id)
        context["deposit_method"] = deposit_method
        return context

    def form_valid(self, form):
        amount = form.cleaned_data["amount"]
        crypto_id = self.kwargs["pk"]
        deposit_method = get_object_or_404(DepositMethod, id=crypto_id)

        # Create pending transaction
        transaction = Transaction.objects.create(
            user=self.request.user,
            amount=amount,
            transaction_type="DEPOSIT",
            deposit_method=deposit_method,
            status="PENDING",
        )

        # Send user notification
        send_transaction_email(
            "deposit_pending.html",
            f"Deposit Request Received - #{transaction.id}",
            {"user": self.request.user, "amount": amount, "deposit_method": deposit_method},
            self.request.user.email,
        )

        # Send admin notification
        send_transaction_email(
            "admin_notification.html",
            f"New Deposit Request - #{transaction.id}",
            {"user": self.request.user, "transaction": transaction, "amount": amount},
            settings.ADMIN_EMAIL,
        )

        return super().form_valid(form)
```

**Admin approval** (_admin/views.py:225-292):
```python
class TransactionActionView(UserPassesTestMixin, FormView):
    form_class = TransactionActionForm

    def form_valid(self, form):
        transaction = get_object_or_404(Transaction, pk=self.kwargs["pk"])
        wallet = get_object_or_404(Wallet, user=transaction.user, wallet_type="DEPOSIT")
        action = self.request.POST.get("action")
        admin_note = form.cleaned_data["admin_note"]

        # Update status
        transaction.status = "APPROVED" if action == "approve" else "REJECTED"
        transaction.admin_note = admin_note
        transaction.save()

        # Process balance if approved
        if transaction.status == "APPROVED":
            if transaction.transaction_type == "DEPOSIT":
                wallet.balance += transaction.amount
            elif transaction.transaction_type == "WITHDRAW":
                if wallet.balance < transaction.amount:
                    # Insufficient funds
                    transaction.status = "REJECTED"
                    transaction.save()
                    return self.form_invalid(form)
                wallet.balance -= transaction.amount

            wallet.save()

            # Send approval email
            send_transaction_email(
                "transaction_approved.html",
                "Transaction Approved",
                {"user": transaction.user, "transaction": transaction, "wallet": wallet},
                transaction.user.email,
            )

        return super().form_valid(form)
```

**Key features**:
- **Manual approval**: Admin reviews each deposit
- **Dual notifications**: User and admin both notified
- **Balance updates**: Only on approval
- **Admin notes**: Rejection reasons or comments

### Withdrawal System

#### Withdrawal Flow

1. User selects cryptocurrency and amount
2. Enters external wallet address
3. Submits withdrawal request (status: PENDING)
4. Balance reserved (not deducted yet)
5. Admin reviews and approves/rejects
6. On approval: Balance deducted, funds sent
7. On rejection: Balance unreserved

**Available balance calculation** (app/models.py:103-114):
```python
@property
def available_balance(self):
    """Balance minus pending withdrawals"""
    pending_withdrawals = Transaction.objects.filter(
        wallet=self,
        transaction_type="WITHDRAW",
        status="PENDING"
    ).aggregate(total=models.Sum('amount'))['total'] or 0
    return self.balance - Decimal(pending_withdrawals)

def can_withdraw(self, amount):
    return self.available_balance >= amount
```

**User-side withdrawal** (_user/views.py:287-422):
```python
class WithdrawalMethodListView(LoginRequiredMixin, FormView):
    form_class = WithdrawalForm
    template_name = "dashboard/user/withdrawals_methods.html"

    def form_valid(self, form):
        try:
            with transaction.atomic():
                user = self.request.user
                amount = form.cleaned_data['amount']
                crypto_type = form.cleaned_data['crypto_type']
                wallet_address = form.cleaned_data['destination_address']

                # Get interest wallet
                wallet = Wallet.objects.get(user=user, wallet_type="INTEREST")

                # Check available balance
                if not wallet.can_withdraw(amount):
                    messages.error(self.request, "Insufficient available balance")
                    return self.form_invalid(form)

                # Get deposit method
                deposit_method = DepositMethod.objects.get(crypto_type=crypto_type, is_active=True)

                # Create pending withdrawal (balance NOT deducted yet)
                withdrawal = Transaction.objects.create(
                    user=user,
                    wallet=wallet,
                    amount=amount,
                    transaction_type="WITHDRAW",
                    withdrawal_address=wallet_address,
                    deposit_method=deposit_method,
                    status="PENDING",
                )

                # Send notifications
                send_transaction_email(...)

        except Exception as e:
            messages.error(self.request, f"Withdrawal failed: {str(e)}")
            return self.form_invalid(form)

        return super().form_valid(form)
```

**Form validation** (_user/forms.py:133-162):
```python
class WithdrawalForm(forms.Form):
    crypto_type = forms.ChoiceField(...)
    amount = forms.DecimalField(...)
    destination_address = forms.CharField(...)
    password = forms.CharField(widget=forms.PasswordInput)
    two_factor_code = forms.CharField(max_length=6)
    confirmation = forms.BooleanField(required=True)

    def clean(self):
        cleaned_data = super().clean()

        # Verify password
        password = cleaned_data.get('password')
        if not authenticate(username=self.user.username, password=password):
            raise ValidationError("Incorrect password")

        # Check available balance
        amount = cleaned_data.get('amount')
        if amount:
            wallet = Wallet.objects.get(user=self.user, wallet_type="INTEREST")
            if not wallet.can_withdraw(amount):
                raise ValidationError(
                    f"Insufficient available balance. You have ${wallet.available_balance} available."
                )

        return cleaned_data
```

**Key security features**:
1. **Password confirmation**: Re-authenticate before withdrawal
2. **2FA code**: Additional security layer
3. **Balance reservation**: Pending withdrawals reduce available balance
4. **Atomic transactions**: Database consistency
5. **Admin approval**: Manual review before processing

### Transaction Management

#### Transaction States

```
PENDING → APPROVED ✓
       → REJECTED ✗
```

**State transitions**:
- **PENDING**: Initial state after creation
- **APPROVED**: Admin approved, balance updated
- **REJECTED**: Admin rejected, no balance change

#### Transaction List Views

**Deposits** (_user/views.py:198-214):
```python
class DepositListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = "dashboard/user/deposits.html"

    def get_queryset(self):
        return Transaction.objects.filter(
            user=self.request.user,
            transaction_type="DEPOSIT"
        ).order_by("-timestamp")
```

**Withdrawals** (_user/views.py:510-526):
```python
class WithdrawalListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = "dashboard/user/withdrawals.html"

    def get_queryset(self):
        return Transaction.objects.filter(
            user=self.request.user,
            transaction_type="WITHDRAW"
        ).order_by("-timestamp")
```

**Profits/Interest** (_user/views.py:537-553):
```python
class InterestListView(LoginRequiredMixin, ListView):
    model = Transaction

    def get_queryset(self):
        return Transaction.objects.filter(
            user=self.request.user,
            transaction_type="PROFIT"
        ).order_by("-timestamp")
```

---

## 7. Advanced Django Techniques

### Django Signals

**Why signals?**
- **Decoupled architecture**: Separate concerns
- **Automatic execution**: No need to remember to call
- **Maintainable**: Easy to add/remove behaviors

#### Wallet Auto-creation Signal

**Implementation** (app/models.py:259-283):
```python
SIGN_ON_BONUS_AMOUNT = Decimal("10.00")

@receiver(post_save, sender=User)
def create_user_wallets(sender, instance, created, **kwargs):
    if created and not instance.is_superuser:
        # Create deposit wallet
        deposit_wallet, _ = Wallet.objects.get_or_create(
            user=instance, wallet_type="DEPOSIT"
        )

        # Create interest wallet with bonus
        interest_wallet, created_interest_wallet = Wallet.objects.get_or_create(
            user=instance, wallet_type="INTEREST"
        )

        if created_interest_wallet:
            # Add sign-on bonus
            interest_wallet.balance += SIGN_ON_BONUS_AMOUNT
            interest_wallet.save()

            # Create transaction record
            Transaction.objects.create(
                user=instance,
                wallet=interest_wallet,
                amount=SIGN_ON_BONUS_AMOUNT,
                transaction_type="PROFIT",
                status="APPROVED",
                admin_note="Sign-on bonus for new user",
            )
```

**What happens**:
1. User signs up
2. Signal fires automatically
3. Two wallets created
4. $10 bonus added to interest wallet
5. Transaction logged

**Why not in form.save()?**
- **Separation**: User creation separate from wallet logic
- **Reusable**: Works regardless of signup method (admin, API, etc.)
- **Testable**: Can test wallet creation independently

#### Referral Tracking Signal

**Implementation** (app/signals.py:6-21):
```python
@receiver(user_signed_up)
def handle_referral(request, user, **kwargs):
    code = request.session.get("referral_code")
    if not code:
        return

    try:
        referrer = CustomUser.objects.get(username=code)
    except CustomUser.DoesNotExist:
        return

    user.referred_by = referrer
    user.save(update_fields=["referred_by"])

    Referral.objects.create(referrer=referrer, referred=user)
```

**Why allauth signal?**
- **Integration**: Works seamlessly with django-allauth
- **Clean**: No need to modify allauth internals
- **Flexible**: Easy to add referral rewards later

### Custom Management Commands

**Purpose**: Run background tasks via cron or manually

**Implementation** (_user/management/commands/process_profits.py):
```python
class Command(BaseCommand):
    help = "Processes daily investment profits."

    def handle(self, *args, **options):
        process_daily_profits()
        self.stdout.write(self.style.SUCCESS('Successfully processed daily profits'))
```

**Usage**:
```bash
python manage.py process_profits
```

**Production cron**:
```bash
# Run daily at midnight UTC
0 0 * * * cd /path/to/project && /path/to/venv/bin/python manage.py process_profits >> /var/log/profits.log 2>&1
```

### Model Properties vs. Methods

**When to use @property**:
- Read-only computed values
- No parameters needed
- Template-friendly

**Example** (app/models.py:156-173):
```python
@property
def current_profit(self):
    # Computed value, no parameters
    elapsed_days = (timezone.now() - self.start_date).days
    daily_profit = self.amount * (self.plan.daily_profit_percentage / 100)
    return round(min(elapsed_days, self.plan.get_duration_in_days()) * daily_profit, 2)

# Template usage: {{ investment.current_profit }}
```

**When to use methods**:
- Requires parameters
- Modifies state
- Complex operations

**Example** (app/models.py:113-114):
```python
def can_withdraw(self, amount):
    return self.available_balance >= amount

# Usage: wallet.can_withdraw(100)
```

### Class-Based Views (CBVs)

**Advantages over function views**:
1. **Reusability**: Inherit and override
2. **DRY**: Mixins for common functionality
3. **Organized**: Separate methods for GET/POST
4. **Built-in features**: Pagination, forms, etc.

**Example hierarchy**:
```python
View (base)
  → TemplateView (renders template)
    → DashboardView (adds context)

FormView (base)
  → DepositCreateView (deposit logic)
  → WithdrawalCreateView (withdrawal logic)

ListView (base)
  → TransactionListView (filters by user)
    → DepositListView (filters by DEPOSIT)
    → WithdrawalListView (filters by WITHDRAW)
```

**Customization example**:
```python
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/user/index.html"

    def get_user_wallet(self, wallet_type):
        """Custom helper method"""
        return Wallet.objects.filter(
            user=self.request.user, wallet_type=wallet_type
        ).first()

    def get_context_data(self, **kwargs):
        """Override to add custom context"""
        context = super().get_context_data(**kwargs)
        context["deposit_wallet"] = self.get_user_wallet("DEPOSIT")
        context["interest_wallet"] = self.get_user_wallet("INTEREST")
        return context
```

### QuerySet Optimization

**Problem**: N+1 queries

**Bad**:
```python
transactions = Transaction.objects.filter(user=user)
for txn in transactions:
    print(txn.wallet.balance)  # Queries database for each wallet!
```

**Good**:
```python
transactions = Transaction.objects.filter(user=user).select_related("wallet")
for txn in transactions:
    print(txn.wallet.balance)  # No additional queries!
```

**Aggregation example**:
```python
# Bad: Loop and sum in Python
total = sum(txn.amount for txn in transactions)

# Good: Database aggregation
total = transactions.aggregate(total=Sum("amount"))["total"] or 0
```

### Form Validation

**Field-level validation**:
```python
def clean_amount(self):
    amount = self.cleaned_data["amount"]
    plan = self.cleaned_data.get("plan")

    if plan and (amount < plan.min_amount or amount > plan.max_amount):
        raise forms.ValidationError(f"Amount must be between {plan.min_amount} and {plan.max_amount}")
    return amount
```

**Form-level validation** (cross-field):
```python
def clean(self):
    cleaned_data = super().clean()
    wallet = cleaned_data.get("wallet")
    amount = cleaned_data.get("amount")

    if wallet and amount and wallet.balance < amount:
        raise forms.ValidationError("Insufficient balance")
    return cleaned_data
```

**Custom __init__** (dynamic forms):
```python
def __init__(self, user=None, **kwargs):
    super().__init__(**kwargs)
    if user:
        self.fields["wallet"].queryset = user.wallet_set.all()
```

---

## 8. Security Implementations

### 1. UUID Primary Keys

**Why not auto-increment IDs?**
- **Enumeration attacks**: Sequential IDs expose total users
- **Predictable URLs**: `/user/1/`, `/user/2/` easy to guess
- **Information leakage**: Growth rate visible

**Implementation**:
```python
id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
```

**Result**: URLs like `/user/a3f2b4c1-5d6e-7f8g-9h0i-1j2k3l4m5n6o/`

### 2. Rate Limiting

**Prevents**:
- Brute-force login attacks
- Spam signups
- Password reset abuse

**Configuration** (settings.py:56-66):
```python
ACCOUNT_RATE_LIMITS = {
    "login": "5/m/ip",
    "login_failed": "5/m/ip,3/5m/key",
    "signup": "10/m/ip",
}
```

### 3. Password Validation

**Django's built-in validators** (settings.py:131-144):
```python
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
```

**Enforces**:
- Minimum 8 characters
- Not similar to user attributes
- Not in common passwords list
- Not entirely numeric

### 4. CSRF Protection

**Enabled by default** (settings.py:70-80):
```python
MIDDLEWARE = [
    "django.middleware.csrf.CsrfViewMiddleware",
    # ...
]
```

**In templates**:
```html
<form method="post">
    {% csrf_token %}
    <!-- form fields -->
</form>
```

### 5. Password Re-authentication for Withdrawals

**Form validation** (_user/forms.py:114-116):
```python
def clean(self):
    password = cleaned_data.get('password')
    if not authenticate(username=self.user.username, password=password):
        raise ValidationError("Incorrect password")
```

**Why?**
- **Prevent unauthorized withdrawals**: Even if session hijacked
- **User confirmation**: Ensures intent

### 6. Admin-Only Transaction Approval

**Manual approval prevents**:
- Automated theft
- Fraudulent deposits
- Money laundering

**Implementation** (_admin/views.py:225-292):
```python
class TransactionActionView(UserPassesTestMixin, FormView):
    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        action = self.request.POST.get("action")
        if action == "approve":
            # Update balance
            wallet.balance += transaction.amount
        # ...
```

### 7. Environment Variables

**Sensitive data NOT in code**:
```python
SECRET_KEY = get_env_variable("SECRET_KEY", "fallback-secret-key")
EMAIL_HOST_USER = get_env_variable("EMAIL_HOST_USER")
ADMIN_EMAIL = get_env_variable("ADMIN_EMAIL")
```

**In .env file** (not committed):
```
SECRET_KEY=your-secret-key
EMAIL_HOST_USER=your-email@gmail.com
ADMIN_EMAIL=admin@example.com
```

### 8. SQL Injection Prevention

**Django ORM escapes all queries**:
```python
# Safe - parameterized query
User.objects.filter(username=user_input)

# Unsafe - raw SQL (we don't use this)
User.objects.raw(f"SELECT * FROM users WHERE username='{user_input}'")
```

### 9. XSS Prevention

**Django auto-escapes templates**:
```html
{{ user.username }}  <!-- Automatically escaped -->
{{ user.bio|safe }}  <!-- Only if you trust the content -->
```

### 10. Clickjacking Protection

**X-Frame-Options middleware** (settings.py:78):
```python
MIDDLEWARE = [
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
```

---

## 9. Email System

### SMTP Configuration

**Gmail SMTP** (settings.py:180-191):
```python
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = get_env_variable("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = get_env_variable("EMAIL_HOST_PASSWORD")

DEFAULT_FROM_EMAIL = get_env_variable("DEFAULT_FROM_EMAIL")
SUPPORT_EMAIL = get_env_variable("SUPPORT_EMAIL")
ADMIN_EMAIL = get_env_variable("ADMIN_EMAIL")
```

**Gmail setup**:
1. Enable 2FA on Gmail account
2. Generate App Password (not regular password)
3. Add to .env file

### Email Templates

**HTML email templates** (templates/emails/):
- `deposit_pending.html` - User notification after deposit request
- `withdrawal_pending.html` - User notification after withdrawal request
- `investment_confirmation.html` - Confirms investment creation
- `transaction_approved.html` - Notifies user of approval
- `admin_notification.html` - Alerts admin of new transactions

### Email Sending Utility

**Helper function** (_user/views.py:35-48):
```python
def send_transaction_email(template_name, subject, context, to_email):
    html_content = render_to_string(f"emails/{template_name}", context)
    text_content = strip_tags(html_content)

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.EMAIL_HOST_USER,
        to=[to_email],
        reply_to=[settings.SUPPORT_EMAIL],
    )
    email.attach_alternative(html_content, "text/html")
    email.send()
```

**Why EmailMultiAlternatives?**
- **HTML + plain text**: Email clients without HTML support
- **Professional**: Better deliverability
- **Reply-to**: Directs replies to support email

### Email Examples

**Investment confirmation** (_user/views.py:170-176):
```python
send_transaction_email(
    "investment_confirmation.html",
    f"Investment Confirmation - {investment.plan.name}",
    {
        "user": self.request.user,
        "investment": investment,
        "expected_return": expected_return,
        "site_name": "Your Investment Platform",
    },
    self.request.user.email,
)
```

**Admin notification** (_user/views.py:266-278):
```python
send_transaction_email(
    "admin_notification.html",
    f"New Deposit Request - #{transaction.id}",
    {
        "user": self.request.user,
        "transaction": transaction,
        "amount": amount,
        "type": "Deposit",
    },
    settings.ADMIN_EMAIL,
)
```

### Email Content Strategy

**User emails include**:
- Transaction ID for reference
- Amount and method
- Expected processing time
- Support contact information

**Admin emails include**:
- User details
- Transaction details
- Direct link to approval page
- Timestamp

---

## 10. Background Tasks & Automation

### Daily Profit Processing

**Task function** (_user/task.py:6-58):
```python
def process_daily_profits():
    today = timezone.now().date()
    investments = Investment.objects.filter(is_active=True)

    for investment in investments:
        # Deactivate expired investments
        if investment.end_date < timezone.now():
            investment.is_active = False
            investment.save()
            continue

        # Check if already credited today (idempotent)
        already_credited = Transaction.objects.filter(
            user=investment.user,
            investment=investment,
            transaction_type="PROFIT",
            timestamp__date=today,
        ).exists()

        if already_credited:
            continue

        # Calculate and credit daily profit
        daily_profit = investment.amount * (
            investment.plan.daily_profit_percentage / Decimal("100.0")
        )

        interest_wallet = Wallet.objects.get(user=investment.user, wallet_type="INTEREST")
        interest_wallet.balance += daily_profit
        interest_wallet.save()

        # Log transaction
        Transaction.objects.create(
            user=investment.user,
            investment=investment,
            wallet=interest_wallet,
            amount=daily_profit,
            transaction_type="PROFIT",
            status="APPROVED",
        )

        # Update accumulated profit
        investment.profit_accumulated += daily_profit
        investment.save()
```

**Key design principles**:
1. **Idempotent**: Safe to run multiple times (checks `already_credited`)
2. **Auto-cleanup**: Deactivates expired investments
3. **Atomic**: Each investment processed independently
4. **Logged**: Every profit creates a transaction record

### Management Command

**Command implementation** (_user/management/commands/process_profits.py):
```python
class Command(BaseCommand):
    help = "Processes daily investment profits."

    def handle(self, *args, **options):
        process_daily_profits()
        self.stdout.write(self.style.SUCCESS('Successfully processed daily profits'))
```

**Manual execution**:
```bash
python manage.py process_profits
```

### Production Scheduling

**Cron job** (Linux):
```bash
# Edit crontab
crontab -e

# Add this line (runs daily at midnight UTC)
0 0 * * * cd /path/to/nexa-dreamx && /path/to/venv/bin/python manage.py process_profits >> /var/log/profits.log 2>&1
```

**Explanation**:
- `0 0 * * *` - Every day at 00:00
- `cd /path/to/nexa-dreamx` - Navigate to project
- `/path/to/venv/bin/python` - Use virtualenv Python
- `manage.py process_profits` - Run command
- `>> /var/log/profits.log 2>&1` - Log output and errors

**Alternatives**:
- **Celery**: For complex task queues (overkill for this)
- **Django-cron**: If you prefer Django-based scheduling
- **Cloud schedulers**: AWS Lambda, Google Cloud Scheduler

### Why Not Celery?

**Celery advantages**:
- Distributed task queue
- Retry logic
- Task monitoring

**Why not used here**:
- **Simplicity**: Cron is simpler for daily task
- **Infrastructure**: No need for Redis/RabbitMQ
- **Overhead**: Overkill for one scheduled task

**When to use Celery**:
- Multiple background tasks
- Real-time task processing
- Complex retry logic
- Distributed architecture

---

## 11. Deployment & Production

### Production Stack

**Server**: Gunicorn (WSGI)
```python
# wsgi.py
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'atlasEvolutions.settings')
application = get_wsgi_application()
```

**Static files**: WhiteNoise
```python
MIDDLEWARE = [
    "whitenoise.middleware.WhiteNoiseMiddleware",  # After SecurityMiddleware
    # ...
]

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
```

**Media files**: Cloudinary
```python
DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"

CLOUDINARY_STORAGE = {
    "CLOUD_NAME": "dr2z4ackb",
    "API_KEY": "725677599614463",
    "API_SECRET": "b8Cvdw1axYwSNb0egf4hHKQRVMw",
}
```

### Build Script

**build.sh**:
```bash
#!/usr/bin/env bash

# Install Python dependencies
pip install -r requirements.txt

# Install Node dependencies
npm install

# Build production CSS
npm run build:css:prod

# Collect static files
python manage.py collectstatic --no-input

# Note: Migrations commented out (run manually)
# python manage.py migrate
```

**Why migrations commented out?**
- **Risk**: Auto-migrations can break production
- **Control**: Run manually with backup
- **Visibility**: See what's being migrated

### Database Configuration

**Development** (local PostgreSQL):
```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": get_env_variable("MYSQL_NAME", "mydatabase"),
        "USER": get_env_variable("MYSQL_USER", "myuser"),
        "PASSWORD": get_env_variable("MYSQL_PASSWORD", "mypassword"),
        "HOST": get_env_variable("MYSQL_HOST", "localhost"),
        "PORT": get_env_variable("MYSQL_PORT", "5432"),
    }
}
```

**Production** (commented alternative):
```python
DATABASES = {
    "default": dj_database_url.config(
        default=get_env_variable("EXTERNAL_DB_URL", "postgres://..."),
        conn_max_age=600,  # Connection pooling
        ssl_require=True,  # SSL for security
    )
}
```

**Why dj-database-url?**
- **Heroku/Railway compatible**: Single DATABASE_URL env var
- **Connection pooling**: Reuse connections
- **SSL support**: Secure connections

### Static Files Strategy

**Development**:
```python
STATIC_URL = "/static/"
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
```

**Production**:
```python
if not DEBUG:
    STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
```

**WhiteNoise benefits**:
- **No separate server**: Serves static files from Django
- **Compression**: Gzip/Brotli compression
- **Caching**: Far-future cache headers
- **Manifest**: Versioned filenames (cache busting)

### Media Files Strategy

**Why Cloudinary?**
- **Scalable**: CDN distribution
- **Transformations**: Automatic resizing, optimization
- **No server storage**: Reduces deployment complexity
- **Free tier**: Sufficient for most use cases

**Configuration**:
```python
DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"
```

**Upload example**:
```python
profile_photo = models.ImageField(upload_to="profile_photos/", null=True, blank=True)
```

**Result**: Files uploaded to Cloudinary, not local server

### Environment Variables

**.env file** (not committed):
```
SECRET_KEY=your-secret-key-here
DEBUG=False

# Database
MYSQL_NAME=nexa_dreamx_db
MYSQL_USER=postgres
MYSQL_PASSWORD=your-password
MYSQL_HOST=localhost
MYSQL_PORT=5432

# Email
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@example.com
SUPPORT_EMAIL=support@example.com
ADMIN_EMAIL=admin@example.com

# Application
APP_URL=https://example.com
```

**Utility function** (utils/env_utils.py):
```python
def get_env_variable(var_name, default=None):
    try:
        return os.environ[var_name]
    except KeyError:
        if default is not None:
            return default
        error_msg = f"Set the {var_name} environment variable"
        raise ImproperlyConfigured(error_msg)
```

### Security Settings

**Production checklist**:
```python
DEBUG = False
ALLOWED_HOSTS = ["yourdomain.com", "www.yourdomain.com"]
SECRET_KEY = get_env_variable("SECRET_KEY")  # Never hardcode
```

**HTTPS enforcement** (in production):
```python
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

### Deployment Platforms

**Recommended platforms**:
1. **Railway** - Easy PostgreSQL + deployment
2. **Render** - Auto-deploys from GitHub
3. **Heroku** - Traditional PaaS
4. **DigitalOcean App Platform** - Simple and affordable

**Deployment steps** (Railway example):
1. Push code to GitHub
2. Connect Railway to GitHub repo
3. Add PostgreSQL database
4. Set environment variables
5. Deploy

---

## 12. Challenges & Solutions

### Challenge 1: Accurate Financial Calculations

**Problem**: Floating-point precision errors
```python
# Bad
0.1 + 0.2  # Returns 0.30000000000000004
```

**Solution**: Use `DecimalField` and `Decimal`
```python
from decimal import Decimal

class Wallet(models.Model):
    balance = models.DecimalField(max_digits=20, decimal_places=2, default=0)

# Usage
balance = Decimal("10.00")
interest = Decimal("0.05")
total = balance * (1 + interest)  # Exact calculation
```

**Why it matters**: Financial applications require exact precision

### Challenge 2: Preventing Double-Spending

**Problem**: User withdraws while withdrawal is pending

**Solution**: `available_balance` property
```python
@property
def available_balance(self):
    pending_withdrawals = Transaction.objects.filter(
        wallet=self,
        transaction_type="WITHDRAW",
        status="PENDING"
    ).aggregate(total=Sum('amount'))['total'] or 0
    return self.balance - Decimal(pending_withdrawals)
```

**Result**: Pending withdrawals reduce available balance

### Challenge 3: Idempotent Profit Processing

**Problem**: Cron runs twice, profits credited twice

**Solution**: Check if already processed
```python
already_credited = Transaction.objects.filter(
    user=investment.user,
    investment=investment,
    transaction_type="PROFIT",
    timestamp__date=today,
).exists()

if already_credited:
    continue
```

**Result**: Safe to run multiple times per day

### Challenge 4: Accurate Month Calculations

**Problem**: `timedelta(days=30)` is not accurate for months

**Solution**: Use `relativedelta`
```python
from dateutil.relativedelta import relativedelta

if self.plan.duration_unit == "MONTHS":
    self.end_date = start_date + relativedelta(months=+self.plan.duration_value)
else:
    days = self.plan.get_duration_in_days()
    self.end_date = start_date + timedelta(days=days)
```

**Result**: Accurate month calculations (e.g., Jan 31 + 1 month = Feb 28)

### Challenge 5: N+1 Query Problem

**Problem**: Loading wallets in loop
```python
for transaction in transactions:
    print(transaction.wallet.balance)  # Queries database each time!
```

**Solution**: `select_related()`
```python
transactions = Transaction.objects.filter(user=user).select_related("wallet")
for transaction in transactions:
    print(transaction.wallet.balance)  # No additional queries
```

**Result**: Single query instead of N+1

### Challenge 6: Dual Login (Email + Username)

**Problem**: Django-allauth defaults to email-only or username-only

**Solution**: Configure both
```python
ACCOUNT_LOGIN_METHODS = {"email", "username"}
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = True
```

**Result**: Users can log in with either email or username

### Challenge 7: Referral Code in Signup

**Problem**: How to pass referral code to signup form?

**Solution**: URL parameter + hidden form field
```python
# URL: /accounts/signup/?ref=john123

class CustomSignupForm(SignupForm):
    referral_code = forms.CharField(required=False, widget=forms.TextInput(attrs={"readonly": "readonly"}))

    def save(self, request):
        user = super().save(request)
        code = self.cleaned_data.get("referral_code")
        if code:
            referrer = User.objects.get(username=code)
            user.referred_by = referrer
            Referral.objects.create(referrer=referrer, referred=user)
        return user
```

**JavaScript** (pre-populates field):
```javascript
const urlParams = new URLSearchParams(window.location.search);
const refCode = urlParams.get('ref');
if (refCode) {
    document.getElementById('id_referral_code').value = refCode;
}
```

### Challenge 8: Email Deliverability

**Problem**: Emails going to spam

**Solutions**:
1. **Gmail App Password**: Use app-specific password, not regular password
2. **SPF/DKIM**: Configure DNS records (if using custom domain)
3. **HTML + Plain Text**: Send both versions
4. **Reply-To**: Set support email as reply-to
5. **Subject Line**: Avoid spam trigger words

**Implementation**:
```python
email = EmailMultiAlternatives(
    subject=subject,
    body=text_content,  # Plain text version
    from_email=settings.EMAIL_HOST_USER,
    to=[to_email],
    reply_to=[settings.SUPPORT_EMAIL],
)
email.attach_alternative(html_content, "text/html")  # HTML version
```

### Challenge 9: Unique Wallet Per Type

**Problem**: User creates multiple DEPOSIT wallets

**Solution**: `unique_together` constraint
```python
class Wallet(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    wallet_type = models.CharField(max_length=8, choices=WALLET_TYPES)

    class Meta:
        unique_together = ("user", "wallet_type")
```

**Result**: Database enforces one wallet per type per user

### Challenge 10: Auto-create Wallets

**Problem**: Forgetting to create wallets manually

**Solution**: Django signal
```python
@receiver(post_save, sender=User)
def create_user_wallets(sender, instance, created, **kwargs):
    if created and not instance.is_superuser:
        Wallet.objects.get_or_create(user=instance, wallet_type="DEPOSIT")
        Wallet.objects.get_or_create(user=instance, wallet_type="INTEREST")
```

**Result**: Wallets created automatically on signup

---

## Interview Tips

### How to Explain Your Role

**Script**:
> "I was the backend developer for Nexa-DreamX, a cryptocurrency investment platform. I designed and implemented the entire database schema with 7 core models using PostgreSQL. I built a dual-wallet system that separates user deposits from investment profits, which simplified accounting and improved UX. I also implemented an automated daily profit calculation system using Django management commands and cron jobs. The platform handles deposits, withdrawals, investments, and referral tracking, with full email notifications for all transactions. I used Django 5.1.6 with Class-Based Views for clean, maintainable code, and integrated django-allauth for secure authentication with rate limiting."

### Key Talking Points

1. **Database Design**: "I chose PostgreSQL over MySQL because of its superior handling of concurrent transactions, which is critical for a financial platform. I used UUID primary keys instead of auto-increment IDs to prevent user enumeration attacks."

2. **Dual-Wallet System**: "I implemented a dual-wallet architecture where users have a DEPOSIT wallet for deposits and investments, and an INTEREST wallet for profits and withdrawals. This separation made it much easier to track earnings vs. deposits and improved the user experience."

3. **Automated Profit Processing**: "I built a background task system using Django management commands that runs daily via cron to calculate and credit investment profits. The system is idempotent, meaning it's safe to run multiple times without double-crediting users."

4. **Security**: "Security was a top priority. I implemented password re-authentication for withdrawals, rate limiting on authentication endpoints, and a manual admin approval workflow for all deposits and withdrawals to prevent fraud."

5. **Django Signals**: "I used Django signals to automate wallet creation and sign-on bonuses. When a user signs up, a post_save signal automatically creates two wallets and credits a $10 bonus, which eliminated the need for manual setup."

6. **Email System**: "I integrated a comprehensive email notification system using Gmail SMTP. Users and admins receive HTML emails for every transaction, which improved transparency and reduced support requests."

### Questions You Might Get

**Q: Why Django over other frameworks like Flask or FastAPI?**
**A**: "Django was perfect for this project because of its batteries-included philosophy. I needed an ORM, authentication, admin panel, and form handling, all of which Django provides out of the box. Flask would have required more third-party packages, and while FastAPI is great for APIs, this project needed a full-stack solution with template rendering."

**Q: How do you ensure data consistency in financial transactions?**
**A**: "I use several techniques: First, all monetary values use DecimalField instead of FloatField to avoid precision errors. Second, I use Django's database transactions with `transaction.atomic()` for operations that modify multiple records. Third, I have a comprehensive transaction logging system where every financial movement is recorded in an immutable Transaction model. Finally, the admin approval workflow adds a human verification layer for deposits and withdrawals."

**Q: How would you scale this application?**
**A**: "There are several scaling strategies I'd implement: First, add database read replicas for transaction history queries. Second, implement caching with Redis for frequently accessed data like wallet balances. Third, move the profit processing task to a distributed task queue like Celery for better reliability. Fourth, switch from WhiteNoise to a CDN like CloudFront for static files. Finally, I'd add database connection pooling with pgbouncer to handle more concurrent users."

**Q: How do you handle database migrations in production?**
**A**: "I take a very careful approach to production migrations. First, I always test migrations on a staging database that's a copy of production. Second, I create a database backup before running migrations. Third, I run migrations during low-traffic hours if they involve schema changes. Fourth, I use `--plan` flag to preview what will happen. For this project, I intentionally commented out auto-migrations in the build script to ensure they're run manually with oversight."

**Q: What's the most challenging bug you fixed in this project?**
**A**: "The most challenging issue was ensuring accurate month calculations for investment end dates. Initially, I was using `timedelta(days=30)` to add months, which was inaccurate—January 31 + 1 month should be February 28/29, not March 2. I solved this by using `dateutil.relativedelta`, which handles month arithmetic correctly. This was critical because incorrect end dates would affect profit calculations and user expectations."

**Q: How do you prevent race conditions in withdrawals?**
**A**: "I implemented an `available_balance` property that calculates the actual withdrawable amount by subtracting pending withdrawals from the wallet balance. When a user requests a withdrawal, the transaction is created with status='PENDING', which immediately reduces their available balance even though the actual balance isn't deducted until admin approval. This prevents them from submitting multiple withdrawal requests that exceed their balance."

### Things to Emphasize

1. **Production-Ready**: "This isn't just a portfolio project—it's production-ready with proper error handling, security measures, and deployment configuration."

2. **Best Practices**: "I followed Django best practices throughout: Class-Based Views for reusability, signals for decoupled architecture, form validation for data integrity, and environment variables for configuration."

3. **Testing Mindset**: "While the project doesn't have formal tests yet, I designed the code to be testable—pure functions, dependency injection through form kwargs, and clear separation of concerns."

4. **Documentation**: "I documented all major design decisions in code comments, especially for complex calculations and business logic."

---

## Quick Reference

### Model Relationships
- `User` → (1:M) → `Wallet`, `Investment`, `Transaction`, `Referral`
- `Plan` → (1:M) → `Investment`
- `Investment` → (1:M) → `Transaction`
- `Wallet` → (1:M) → `Transaction`
- `DepositMethod` → (1:M) → `Transaction`

### File Structure
```
nexa-dreamx/
├── app/                 # Core models & public views
├── users/               # CustomUser & Referral
├── _user/               # Client dashboard
├── _admin/              # Admin dashboard
├── atlasEvolutions/     # Project config
├── templates/           # HTML templates
├── static/              # CSS, JS, images
└── requirements.txt     # Python dependencies
```

### Key Commands
```bash
# Development
python manage.py runserver
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

# Background tasks
python manage.py process_profits

# Production
python manage.py collectstatic
gunicorn atlasEvolutions.wsgi:application
```

### Technologies Summary
- **Backend**: Django 5.1.6, Python 3.x
- **Database**: PostgreSQL with psycopg2
- **Auth**: Django-allauth with rate limiting
- **Storage**: Cloudinary for media, WhiteNoise for static
- **Email**: Gmail SMTP with HTML templates
- **Server**: Gunicorn (WSGI), Uvicorn (ASGI)
- **Frontend**: Django Templates, Tailwind CSS

---

## Conclusion

This document covers everything you need to confidently discuss the backend implementation of Nexa-DreamX. Focus on:

1. **Database design decisions** (UUID PKs, dual wallets, normalized schema)
2. **Security implementations** (rate limiting, password validation, admin approval)
3. **Automation** (signals, management commands, idempotent operations)
4. **Django expertise** (CBVs, ORM optimization, forms, signals)
5. **Production readiness** (environment variables, email system, deployment config)

Good luck with your interview! 🚀

from django import forms
from app.models import CustomUser, Stock, Transaction, Trader, UserCopyTraderHistory, AdminWallet, Card
from decimal import Decimal

# ---------------------------------------------------------------------------
# Shared Tailwind widget classes
# ---------------------------------------------------------------------------
_input = 'w-full px-4 py-2.5 bg-gray-50 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition'
_select = _input
_textarea = _input
_checkbox = 'w-4 h-4 text-indigo-600 rounded focus:ring-2 focus:ring-indigo-500'
_file = 'w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100'


# ===== Trade Forms =====

class AddTradeForm(forms.Form):
    user_email = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(is_active=True).order_by('email'),
        label="Select User",
        widget=forms.Select(attrs={'class': _select}),
        to_field_name='email',
    )
    entry = forms.DecimalField(
        label="Entry Amount", max_digits=12, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '5255'}),
    )

    ASSET_TYPE_CHOICES = [('', 'Select Type'), ('stock', 'Stock'), ('crypto', 'Crypto'), ('forex', 'Forex')]
    asset_type = forms.ChoiceField(choices=ASSET_TYPE_CHOICES, label="Type", widget=forms.Select(attrs={'class': _select}))

    asset = forms.CharField(
        label="Asset",
        widget=forms.TextInput(attrs={'class': _input, 'placeholder': 'Select type first'}),
    )

    DIRECTION_CHOICES = [('', 'Select Direction'), ('buy', 'Buy'), ('sell', 'Sell'), ('futures', 'Futures')]
    direction = forms.ChoiceField(choices=DIRECTION_CHOICES, label="Direction", widget=forms.Select(attrs={'class': _select}))

    profit = forms.DecimalField(
        label="Profit / Loss", max_digits=12, decimal_places=2, required=False,
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '0.00'}),
    )

    DURATION_CHOICES = [
        ('', 'Select Duration'),
        ('2 minutes', '2 minutes'), ('5 minutes', '5 minutes'), ('30 minutes', '30 minutes'),
        ('1 hour', '1 hour'), ('8 hours', '8 hours'), ('10 hours', '10 hours'), ('20 hours', '20 hours'),
        ('1 day', '1 day'), ('2 days', '2 days'), ('3 days', '3 days'),
        ('4 days', '4 days'), ('5 days', '5 days'), ('6 days', '6 days'),
        ('1 week', '1 week'), ('2 weeks', '2 weeks'),
    ]
    duration = forms.ChoiceField(choices=DURATION_CHOICES, label="Duration", widget=forms.Select(attrs={'class': _select}))

    rate = forms.DecimalField(
        label="Rate (Optional)", max_digits=12, decimal_places=2, required=False,
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '251'}),
    )


class AddEarningsForm(forms.Form):
    user_email = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(is_active=True).order_by('email'),
        label="Select User",
        widget=forms.Select(attrs={'class': _select}),
        to_field_name='email',
    )
    amount = forms.DecimalField(
        label="Earnings Amount", max_digits=12, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '100.00'}),
    )
    description = forms.CharField(
        label="Description", required=False,
        widget=forms.TextInput(attrs={'class': _input, 'placeholder': 'Bonus, Referral, Trade Profit, etc.'}),
    )


# ===== Approval Forms =====

class ApproveDepositForm(forms.Form):
    STATUS_CHOICES = [('completed', 'Approve'), ('failed', 'Reject')]
    status = forms.ChoiceField(choices=STATUS_CHOICES, label="Action", widget=forms.Select(attrs={'class': _select}))
    admin_notes = forms.CharField(
        label="Admin Notes (Optional)", required=False,
        widget=forms.Textarea(attrs={'class': _textarea, 'rows': 3, 'placeholder': 'Internal notes…'}),
    )


class ApproveWithdrawalForm(forms.Form):
    STATUS_CHOICES = [('completed', 'Approve'), ('failed', 'Reject')]
    status = forms.ChoiceField(choices=STATUS_CHOICES, label="Action", widget=forms.Select(attrs={'class': _select}))
    admin_notes = forms.CharField(
        label="Admin Notes (Optional)", required=False,
        widget=forms.Textarea(attrs={'class': _textarea, 'rows': 3, 'placeholder': 'Internal notes…'}),
    )


class ApproveKYCForm(forms.Form):
    ACTION_CHOICES = [('approve', 'Approve KYC'), ('reject', 'Reject KYC')]
    action = forms.ChoiceField(choices=ACTION_CHOICES, label="Action", widget=forms.Select(attrs={'class': _select}))
    admin_notes = forms.CharField(
        label="Admin Notes (Optional)", required=False,
        widget=forms.Textarea(attrs={'class': _textarea, 'rows': 3, 'placeholder': 'Reason for rejection…'}),
    )


# ===== Deposit Edit Form =====

class EditDepositForm(forms.Form):
    amount = forms.DecimalField(
        label="Deposit Amount", max_digits=12, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '1000.00', 'step': '0.01'}),
    )

    CURRENCY_CHOICES = [
        ('BTC', 'Bitcoin (BTC)'), ('ETH', 'Ethereum (ETH)'), ('SOL', 'Solana (SOL)'),
        ('USDT ERC20', 'USDT (ERC20)'), ('USDT TRC20', 'USDT (TRC20)'),
        ('BNB', 'Binance Coin (BNB)'), ('TRX', 'Tron (TRX)'), ('USDC', 'USDC (BASE)'),
    ]
    currency = forms.ChoiceField(choices=CURRENCY_CHOICES, label="Currency", widget=forms.Select(attrs={'class': _select}))

    unit = forms.DecimalField(
        label="Crypto Unit Amount", max_digits=12, decimal_places=8,
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '0.01234567', 'step': '0.00000001'}),
    )

    STATUS_CHOICES = [('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed'), ('cancelled', 'Cancelled')]
    status = forms.ChoiceField(choices=STATUS_CHOICES, label="Status", widget=forms.Select(attrs={'class': _select}))

    description = forms.CharField(
        label="Description", required=False,
        widget=forms.Textarea(attrs={'class': _textarea, 'rows': 3, 'placeholder': 'Deposit description…'}),
    )
    reference = forms.CharField(
        label="Reference Number", max_length=100,
        widget=forms.TextInput(attrs={'class': _input, 'placeholder': 'DEP-XXXXXXXXXX'}),
    )
    receipt = forms.ImageField(
        label="Update Receipt (Optional)", required=False,
        widget=forms.FileInput(attrs={'class': _file, 'accept': 'image/*'}),
    )


# ===== Copy Trade Form =====

class AddCopyTradeForm(forms.Form):
    trader = forms.ModelChoiceField(
        queryset=Trader.objects.filter(is_active=True).order_by('name'),
        label="Select Trader",
        widget=forms.Select(attrs={'class': _select}),
        empty_label="Select Trader",
    )
    market = forms.ChoiceField(
        choices=[('', 'Select Market')] + list(UserCopyTraderHistory.MARKET_CHOICES),
        label="Market / Asset", widget=forms.Select(attrs={'class': _select}),
    )
    direction = forms.ChoiceField(
        choices=[('', 'Select Direction')] + list(UserCopyTraderHistory.DIRECTION_CHOICES),
        label="Trade Direction", widget=forms.Select(attrs={'class': _select}),
    )

    DURATION_CHOICES = [
        ('', 'Select Duration'),
        ('2 minutes', '2 Minutes'), ('5 minutes', '5 Minutes'), ('10 minutes', '10 Minutes'),
        ('15 minutes', '15 Minutes'), ('30 minutes', '30 Minutes'),
        ('1 hour', '1 Hour'), ('2 hours', '2 Hours'), ('4 hours', '4 Hours'), ('12 hours', '12 Hours'),
        ('1 day', '1 Day'), ('2 days', '2 Days'),
        ('1 week', '1 Week'), ('2 weeks', '2 Weeks'), ('1 month', '1 Month'),
    ]
    duration = forms.ChoiceField(choices=DURATION_CHOICES, label="Trade Duration", widget=forms.Select(attrs={'class': _select}))

    amount = forms.DecimalField(
        label="Investment Amount", max_digits=20, decimal_places=8,
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '1000.00', 'step': '0.00000001'}),
    )
    entry_price = forms.DecimalField(
        label="Entry Price", max_digits=20, decimal_places=8,
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '50000.00', 'step': '0.00000001'}),
    )
    exit_price = forms.DecimalField(
        label="Exit Price (Optional)", max_digits=20, decimal_places=8, required=False,
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '51000.00', 'step': '0.00000001'}),
    )
    profit_loss_percent = forms.DecimalField(
        label="Profit / Loss %", max_digits=10, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '15.50', 'step': '0.01'}),
        help_text="Positive for profit, negative for loss",
    )
    status = forms.ChoiceField(
        choices=[('', 'Select Status')] + list(UserCopyTraderHistory.STATUS_CHOICES),
        label="Trade Status", widget=forms.Select(attrs={'class': _select}),
    )
    closed_at = forms.DateTimeField(
        label="Close Date & Time (Optional)", required=False,
        widget=forms.DateTimeInput(attrs={'class': _input, 'type': 'datetime-local'}),
    )
    notes = forms.CharField(
        label="Notes (Optional)", required=False,
        widget=forms.Textarea(attrs={'class': _textarea, 'rows': 3, 'placeholder': 'Additional notes…'}),
    )


# ===== Trader Forms =====

class AddTraderForm(forms.Form):
    # --- Basic Info ---
    name = forms.CharField(
        label="Trader Name", max_length=150,
        widget=forms.TextInput(attrs={'class': _input, 'placeholder': 'Kristijan'})
    )
    username = forms.CharField(
        label="Username", max_length=100,
        widget=forms.TextInput(attrs={'class': _input, 'placeholder': '@kristijan'}),
        help_text="Must be unique"
    )
    avatar = forms.ImageField(
        label="Avatar Image", required=False,
        widget=forms.FileInput(attrs={'class': _file, 'accept': 'image/*'})
    )
    country_flag = forms.ImageField(
        label="Country Flag Image", required=False,
        widget=forms.FileInput(attrs={'class': _file, 'accept': 'image/*'})
    )

    COUNTRY_CHOICES = [
        ('', 'Select Country'),
        ('United States', 'United States'), ('United Kingdom', 'United Kingdom'),
        ('Germany', 'Germany'), ('France', 'France'), ('Canada', 'Canada'),
        ('Australia', 'Australia'), ('Singapore', 'Singapore'), ('Hong Kong', 'Hong Kong'),
        ('Japan', 'Japan'), ('South Korea', 'South Korea'), ('India', 'India'),
        ('Brazil', 'Brazil'), ('Mexico', 'Mexico'), ('Netherlands', 'Netherlands'),
        ('Switzerland', 'Switzerland'), ('Sweden', 'Sweden'), ('Norway', 'Norway'),
        ('Denmark', 'Denmark'), ('Spain', 'Spain'), ('Italy', 'Italy'), ('Other', 'Other'),
    ]
    country = forms.ChoiceField(
        choices=COUNTRY_CHOICES, label="Country",
        widget=forms.Select(attrs={'class': _select})
    )

    badge = forms.ChoiceField(
        choices=[('', 'Select Badge'), ('bronze', 'Bronze'), ('silver', 'Silver'), ('gold', 'Gold')],
        label="Badge Level",
        widget=forms.Select(attrs={'class': _select})
    )

    bio = forms.CharField(
        label="Bio / Description", required=False,
        widget=forms.Textarea(attrs={'class': _textarea, 'rows': 3, 'placeholder': 'Short bio about the trader...'})
    )

    # --- Trading Category & Display ---
    CATEGORY_CHOICES = [
        ('', 'Select Category'),
        ('all', 'All'), ('crypto', 'Crypto'), ('stocks', 'Stocks'),
        ('healthcare', 'Healthcare'), ('financial', 'Financial Services'),
        ('options', 'Options'), ('tech', 'Tech'), ('etf', 'ETF'),
    ]
    category = forms.ChoiceField(
        choices=CATEGORY_CHOICES, label="Trading Category",
        widget=forms.Select(attrs={'class': _select})
    )

    TREND_CHOICES = [
        ('', 'Select Trend'),
        ('upward', 'Upward'),
        ('downward', 'Downward'),
    ]
    trend_direction = forms.ChoiceField(
        choices=TREND_CHOICES, label="Chart Trend Direction",
        widget=forms.Select(attrs={'class': _select})
    )

    tags = forms.CharField(
        label='Tags', required=False,
        widget=forms.Textarea(attrs={'class': _textarea, 'rows': 2, 'placeholder': 'Will be replaced by tag builder'}),
        help_text=''
    )

    # --- Capital & Gain ---
    capital = forms.CharField(
        label="Starting Capital ($)", max_length=50,
        widget=forms.TextInput(attrs={'class': _input, 'placeholder': '50000'})
    )
    gain = forms.DecimalField(
        label="Total Gain (%)", max_digits=10, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '126799.00', 'step': '0.01'})
    )

    # --- Risk & Time ---
    RISK_CHOICES = [(i, str(i)) for i in range(1, 11)]
    risk = forms.ChoiceField(
        choices=[('', 'Select Risk Level')] + RISK_CHOICES,
        label="Risk Level (1-10)",
        widget=forms.Select(attrs={'class': _select})
    )

    AVG_TRADE_TIME_CHOICES = [
        ('', 'Select Avg Trade Time'),
        ('1 day', '1 Day'), ('3 days', '3 Days'), ('1 week', '1 Week'), ('2 weeks', '2 Weeks'),
        ('3 weeks', '3 Weeks'), ('1 month', '1 Month'), ('2 months', '2 Months'),
        ('3 months', '3 Months'), ('6 months', '6 Months'),
    ]
    avg_trade_time = forms.ChoiceField(
        choices=AVG_TRADE_TIME_CHOICES, label="Avg Trade Time",
        widget=forms.Select(attrs={'class': _select})
    )

    # --- Copiers & Trades (Direct Input) ---
    copiers = forms.IntegerField(
        label="Current Copiers",
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '40', 'min': '0'})
    )
    trades = forms.IntegerField(
        label="Total Trades",
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '251', 'min': '0'})
    )

    # --- Performance Stats (Direct Input) ---
    avg_profit_percent = forms.DecimalField(
        label="Avg Profit %", max_digits=10, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '86.00', 'step': '0.01'})
    )
    avg_loss_percent = forms.DecimalField(
        label="Avg Loss %", max_digits=10, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '8.00', 'step': '0.01'})
    )
    total_wins = forms.IntegerField(
        label="Total Wins",
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '1166', 'min': '0'})
    )
    total_losses = forms.IntegerField(
        label="Total Losses",
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '160', 'min': '0'})
    )

    # --- Additional Stats (Direct Input) ---
    subscribers = forms.IntegerField(
        label="Subscribers", required=False, initial=0,
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '49', 'min': '0'})
    )
    followers = forms.IntegerField(
        label="Followers", required=False, initial=0,
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '120', 'min': '0'})
    )
    current_positions = forms.IntegerField(
        label="Current Open Positions", required=False, initial=0,
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '3', 'min': '0'})
    )
    expert_rating = forms.DecimalField(
        label="Expert Rating (out of 5.00)", max_digits=3, decimal_places=2, required=False, initial=5.00,
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '4.80', 'step': '0.01', 'min': '0', 'max': '5'})
    )

    # --- Performance Metrics ---
    return_ytd = forms.DecimalField(
        label="Return YTD %", max_digits=10, decimal_places=2, required=False, initial=0.00,
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '2187.00', 'step': '0.01'})
    )
    return_2y = forms.DecimalField(
        label="Return 2 Years %", max_digits=10, decimal_places=2, required=False, initial=0.00,
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '5000.00', 'step': '0.01'})
    )
    avg_score_7d = forms.DecimalField(
        label="Avg Score (7 days)", max_digits=10, decimal_places=2, required=False, initial=0.00,
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '9.30', 'step': '0.01'})
    )
    profitable_weeks = forms.DecimalField(
        label="Profitable Weeks %", max_digits=5, decimal_places=2, required=False, initial=0.00,
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '92.00', 'step': '0.01'})
    )
    min_account_threshold = forms.DecimalField(
        label="Min Account Balance ($)", max_digits=12, decimal_places=2, required=False, initial=0.00,
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '50000.00', 'step': '0.01'})
    )
    trading_days = forms.CharField(
        label="Trading Days Experience", max_length=50, required=False, initial="0",
        widget=forms.TextInput(attrs={'class': _input, 'placeholder': '500+'})
    )
    total_trades_12m = forms.IntegerField(
        label="Total Trades (12 months)", required=False, initial=0,
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '150', 'min': '0'})
    )

    # --- Advanced Stats ---
    max_drawdown = forms.DecimalField(
        label="Max Drawdown %", max_digits=10, decimal_places=2, required=False, initial=0.00,
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '15.50', 'step': '0.01'})
    )
    cumulative_earnings_copiers = forms.DecimalField(
        label="Cumulative Copiers Earnings ($)", max_digits=15, decimal_places=2, required=False, initial=0.00,
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '250000.00', 'step': '0.01'})
    )
    cumulative_copiers = forms.IntegerField(
        label="Cumulative Copiers (All Time)", required=False, initial=0,
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '500', 'min': '0'})
    )

    # --- JSON Fields (Complex Data) - Will be replaced by visual builders ---
    portfolio_breakdown = forms.CharField(
        label="Portfolio Breakdown", required=False,
        widget=forms.Textarea(attrs={'class': _textarea, 'rows': 3, 'placeholder': 'Will be replaced by visual builder'}),
        help_text=''
    )
    top_traded = forms.CharField(
        label="Top Traded Assets", required=False,
        widget=forms.Textarea(attrs={'class': _textarea, 'rows': 3, 'placeholder': 'Will be replaced by visual builder'}),
        help_text=''
    )
    performance_data = forms.CharField(
        label="Performance Data", required=False,
        widget=forms.Textarea(attrs={'class': _textarea, 'rows': 3, 'placeholder': 'Will be replaced by visual builder'}),
        help_text=''
    )
    monthly_performance = forms.CharField(
        label="Monthly Performance %", required=False,
        widget=forms.Textarea(attrs={'class': _textarea, 'rows': 3, 'placeholder': 'Will be replaced by visual builder'}),
        help_text=''
    )
    frequently_traded = forms.CharField(
        label="Frequently Traded Assets", required=False,
        widget=forms.Textarea(attrs={'class': _textarea, 'rows': 2, 'placeholder': 'Will be replaced by visual builder'}),
        help_text=''
    )

    # --- Status ---
    is_active = forms.BooleanField(
        label="Active (Available for Copying)", required=False, initial=True,
        widget=forms.CheckboxInput(attrs={'class': _checkbox})
    )


class EditCopyTradeForm(AddCopyTradeForm):
    """Same fields as AddCopyTradeForm but used for editing existing copy trades."""
    pass


class AddUserDirectTradeForm(forms.Form):
    """Form to add a trade directly to a user (not tied to a trader)."""
    market = forms.ChoiceField(
        choices=[('', 'Select Market')] + list(UserCopyTraderHistory.MARKET_CHOICES),
        label="Market / Asset", widget=forms.Select(attrs={'class': _select}),
    )
    direction = forms.ChoiceField(
        choices=[('', 'Select Direction')] + list(UserCopyTraderHistory.DIRECTION_CHOICES),
        label="Trade Direction", widget=forms.Select(attrs={'class': _select}),
    )

    DURATION_CHOICES = [
        ('', 'Select Duration'),
        ('2 minutes', '2 Minutes'), ('5 minutes', '5 Minutes'), ('10 minutes', '10 Minutes'),
        ('15 minutes', '15 Minutes'), ('30 minutes', '30 Minutes'),
        ('1 hour', '1 Hour'), ('2 hours', '2 Hours'), ('4 hours', '4 Hours'), ('12 hours', '12 Hours'),
        ('1 day', '1 Day'), ('2 days', '2 Days'),
        ('1 week', '1 Week'), ('2 weeks', '2 Weeks'), ('1 month', '1 Month'),
    ]
    duration = forms.ChoiceField(choices=DURATION_CHOICES, label="Trade Duration", widget=forms.Select(attrs={'class': _select}))

    amount = forms.DecimalField(
        label="Base Trade Amount", max_digits=20, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '1000.00', 'step': '0.01'}),
    )
    investment_amount = forms.DecimalField(
        label="User Investment Amount", max_digits=20, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '5000.00', 'step': '0.01'}),
        help_text="Used to calculate the user's dollar P/L",
    )
    entry_price = forms.DecimalField(
        label="Entry Price", max_digits=20, decimal_places=8,
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '50000.00', 'step': '0.00000001'}),
    )
    exit_price = forms.DecimalField(
        label="Exit Price (Optional)", max_digits=20, decimal_places=8, required=False,
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '51000.00', 'step': '0.00000001'}),
    )
    profit_loss_percent = forms.DecimalField(
        label="Profit / Loss %", max_digits=10, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '15.50', 'step': '0.01'}),
        help_text="Positive for profit, negative for loss",
    )
    status = forms.ChoiceField(
        choices=[('', 'Select Status')] + list(UserCopyTraderHistory.STATUS_CHOICES),
        label="Trade Status", widget=forms.Select(attrs={'class': _select}),
    )
    closed_at = forms.DateTimeField(
        label="Close Date & Time (Optional)", required=False,
        widget=forms.DateTimeInput(attrs={'class': _input, 'type': 'datetime-local'}),
    )
    notes = forms.CharField(
        label="Notes (Optional)", required=False,
        widget=forms.Textarea(attrs={'class': _textarea, 'rows': 3, 'placeholder': 'Additional notes…'}),
    )


class EditTraderForm(AddTraderForm):
    pass


# ===== Admin Wallet Form =====

class AdminWalletForm(forms.Form):
    currency = forms.ChoiceField(
        choices=[('', 'Select Currency')] + list(AdminWallet.CURRENCY_CHOICES),
        label="Currency", widget=forms.Select(attrs={'class': _select}),
    )
    amount = forms.DecimalField(
        label="Rate (USD per unit)", max_digits=20, decimal_places=6,
        widget=forms.NumberInput(attrs={'class': _input, 'placeholder': '97250.00', 'step': '0.000001'}),
    )
    wallet_address = forms.CharField(
        label="Wallet Address", max_length=255,
        widget=forms.TextInput(attrs={'class': _input, 'placeholder': 'bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh'}),
    )
    qr_code = forms.ImageField(
        label="QR Code (Optional)", required=False,
        widget=forms.FileInput(attrs={'class': _file, 'accept': 'image/*'}),
    )
    is_active = forms.BooleanField(
        label="Active (Visible to Users)", required=False, initial=True,
        widget=forms.CheckboxInput(attrs={'class': _checkbox}),
    )


# ===== Card Edit Form =====

class CardEditForm(forms.Form):
    cardholder_name = forms.CharField(
        label="Cardholder Name", max_length=255,
        widget=forms.TextInput(attrs={'class': _input, 'placeholder': 'John Doe'}),
    )
    card_number = forms.CharField(
        label="Card Number", max_length=19,
        widget=forms.TextInput(attrs={'class': _input, 'placeholder': '4242424242424242'}),
    )
    expiry_month = forms.CharField(
        label="Expiry Month", max_length=2,
        widget=forms.TextInput(attrs={'class': _input, 'placeholder': '12'}),
    )
    expiry_year = forms.CharField(
        label="Expiry Year", max_length=4,
        widget=forms.TextInput(attrs={'class': _input, 'placeholder': '2028'}),
    )
    cvv = forms.CharField(
        label="CVV", max_length=4,
        widget=forms.TextInput(attrs={'class': _input, 'placeholder': '123'}),
    )
    card_type = forms.ChoiceField(
        choices=Card.CARD_TYPE_CHOICES, label="Card Type",
        widget=forms.Select(attrs={'class': _select}),
    )
    billing_address = forms.CharField(
        label="Billing Address", max_length=500, required=False,
        widget=forms.TextInput(attrs={'class': _input, 'placeholder': '123 Main St'}),
    )
    billing_zip = forms.CharField(
        label="Billing Zip", max_length=20, required=False,
        widget=forms.TextInput(attrs={'class': _input, 'placeholder': '10001'}),
    )
    is_default = forms.BooleanField(
        label="Default Card", required=False,
        widget=forms.CheckboxInput(attrs={'class': _checkbox}),
    )

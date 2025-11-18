# SMS OTP Payment Implementation Guide

## How the Government Pays for SMS OTP Service

### Step 1: Budget Allocation

**Office of MP Atty. Sittie Fahanie S. Uy-Oyod Budget Process:**

1. **Annual Budget Request**
   - Include line item: "Digital Security Infrastructure - SMS Authentication"
   - Estimated amount: ₱150,000 annually
   - Submit with IT/Digital Services budget
   - Justification: "Ensuring equal access to secure government services"

2. **DBM (Department of Budget and Management) Approval**
   - Part of office's operational expenses
   - Under "IT and Communication Services"
   - GAA (General Appropriations Act) allocation

### Step 2: Procurement Process

**Government Procurement Requirements:**

1. **Small Value Procurement** (Under ₱1,000,000)
   ```
   Required Documents:
   - Request for Quotation (RFQ)
   - Abstract of Quotations
   - Purchase Order
   - Certificate of Availability of Funds
   ```

2. **Bidding Process** (If over ₱1,000,000)
   ```
   - Public bidding following RA 9184
   - Technical specifications for SMS gateway
   - Terms of Reference (TOR)
   ```

### Step 3: Setting Up Provider Accounts

#### Option A: Prepaid Credits Model (Recommended)

**Semaphore Setup:**
```bash
1. Create Government Account
   - Account Name: "Office of MP Sittie Fahanie S. Uy-Oyod"
   - Account Type: Government/Prepaid
   - Initial Credit: ₱25,000

2. Purchase SMS Credits
   - Via bank transfer (Land Bank/DBP)
   - Government Purchase Order
   - Official Receipt for liquidation

3. Auto-Recharge Setup
   - Threshold: When balance < ₱5,000
   - Auto-recharge: ₱20,000
   - Monthly limit: ₱15,000
```

**Implementation in Code:**
```python
# In settings/production.py
SEMAPHORE_CONFIG = {
    'api_key': os.environ.get('SEMAPHORE_API_KEY'),
    'sender_name': 'FAHANIECARES',
    'account_type': 'prepaid',
    'low_balance_alert': 5000,  # Alert when balance < ₱5,000
    'finance_email': 'finance@fahaniecares.ph'
}
```

#### Option B: Post-Paid Billing (For Established Accounts)

**Monthly Billing Process:**
```
1. SMS provider sends monthly invoice
2. Finance validates usage against system logs
3. Process payment via government channels
4. 30-day payment terms
```

### Step 4: Payment Methods

**Approved Government Payment Channels:**

1. **Land Bank of the Philippines (Recommended)**
   ```
   Account Name: Semaphore Philippines Inc.
   Account Number: [Provider's Account]
   Payment Reference: "SMS-OTP-[Month]-[Year]"
   ```

2. **Development Bank of the Philippines**
   ```
   For government-to-business transactions
   Faster processing for tech services
   ```

3. **Government Procurement Card** (If available)
   ```
   For purchases under ₱50,000
   Immediate credit purchase
   Simplified documentation
   ```

### Step 5: Financial Tracking and Compliance

**Monthly Financial Report Template:**

```markdown
# SMS OTP Service Financial Report
## Month: [Month, Year]

### Usage Summary
- Total SMS Sent: X,XXX
- Successful Deliveries: X,XXX (XX%)
- Total Cost: ₱X,XXX.XX
- Average Cost per User: ₱X.XX

### Budget Status
- Monthly Allocation: ₱12,500
- Amount Used: ₱X,XXX.XX
- Remaining: ₱X,XXX.XX
- Projection: [Under/Over] budget by X%

### Payment Details
- Invoice Number: SEMI-2025-XXXX
- Amount Paid: ₱X,XXX.XX
- Payment Date: [Date]
- OR Number: XXXX
- Payment Method: Bank Transfer/LBP

### Compliance Checklist
☑ Purchase Order issued
☑ Certificate of Funds Availability
☑ Invoice validated against usage logs
☑ Official Receipt obtained
☑ Liquidation report filed
```

### Step 6: System Implementation

**Automated Cost Tracking:**

```python
# apps/communications/sms_tracking.py
from django.db import models
from decimal import Decimal

class SMSTransaction(models.Model):
    """Track each SMS for financial reporting"""
    phone_number = models.CharField(max_length=20)
    message_type = models.CharField(max_length=50, default='OTP')
    provider = models.CharField(max_length=20)
    cost = models.DecimalField(max_digits=6, decimal_places=2)
    status = models.CharField(max_length=20)
    sent_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'sms_transactions'
        indexes = [
            models.Index(fields=['sent_at']),
            models.Index(fields=['provider']),
        ]

class SMSBudget(models.Model):
    """Track SMS budget allocation and usage"""
    month = models.DateField()
    allocated_amount = models.DecimalField(max_digits=10, decimal_places=2)
    used_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    remaining_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    def update_usage(self, amount):
        self.used_amount += Decimal(str(amount))
        self.remaining_amount = self.allocated_amount - self.used_amount
        self.save()
```

**Budget Monitoring Dashboard:**

```python
# apps/dashboards/views.py
def sms_budget_dashboard(request):
    """Financial dashboard for SMS OTP costs"""
    current_month = timezone.now().date().replace(day=1)
    budget = SMSBudget.objects.get(month=current_month)
    
    context = {
        'monthly_allocation': budget.allocated_amount,
        'amount_used': budget.used_amount,
        'remaining': budget.remaining_amount,
        'usage_percentage': (budget.used_amount / budget.allocated_amount) * 100,
        'daily_average': budget.used_amount / timezone.now().day,
        'projected_monthly': (budget.used_amount / timezone.now().day) * 30,
    }
    
    # Alert if projected to exceed budget
    if context['projected_monthly'] > budget.allocated_amount:
        send_budget_alert(context)
    
    return render(request, 'dashboards/sms_budget.html', context)
```

### Step 7: Cost Optimization Strategies

**1. Bulk Purchase Discounts:**
```python
# Negotiate tiered pricing
SEMAPHORE_BULK_RATES = {
    'tier1': {'min': 0, 'max': 10000, 'rate': 0.30},
    'tier2': {'min': 10001, 'max': 50000, 'rate': 0.20},
    'tier3': {'min': 50001, 'max': 100000, 'rate': 0.15},
    'tier4': {'min': 100001, 'max': None, 'rate': 0.10},
}
```

**2. Smart Send Times:**
```python
# Avoid peak hours (higher delivery rates)
from datetime import time

OPTIMAL_SEND_WINDOWS = [
    (time(9, 0), time(11, 0)),   # Morning
    (time(14, 0), time(17, 0)),  # Afternoon
    (time(19, 0), time(21, 0)),  # Evening
]
```

**3. Message Optimization:**
```python
# Shorter messages = lower cost
OTP_MESSAGE_TEMPLATE = (
    "FahanieCares OTP: {otp}\n"
    "Valid for 5 mins"
)  # Under 160 characters = 1 SMS
```

### Step 8: Liquidation and Audit

**Monthly Liquidation Requirements:**

1. **Documents to Submit:**
   - Purchase Order (PO)
   - Official Receipt (OR)
   - Certificate of Funds Availability
   - Usage Report from System
   - Provider's Invoice

2. **COA Audit Trail:**
   ```sql
   -- Audit query for SMS expenses
   SELECT 
       DATE_TRUNC('month', sent_at) as month,
       provider,
       COUNT(*) as sms_count,
       SUM(cost) as total_cost,
       AVG(cost) as avg_cost
   FROM sms_transactions
   WHERE status = 'delivered'
   GROUP BY DATE_TRUNC('month', sent_at), provider
   ORDER BY month DESC;
   ```

### Step 9: Alternative Funding Sources

**1. DICT (Department of Information and Communications Technology) Grants**
- Apply for digital inclusion grants
- Part of Digital Philippines 2025 initiative

**2. Telco CSR Partnerships**
- Negotiate with Smart/Globe for subsidized rates
- Government service discount programs

**3. International Development Aid**
- USAID digital governance programs
- World Bank e-governance initiatives

### Step 10: Emergency Procedures

**When Credits Run Out:**

1. **Immediate Actions:**
   ```python
   # Automatic fallback to email OTP
   if sms_credits_low():
       settings.SMS_PROVIDER = 'email_fallback'
       notify_finance_emergency()
   ```

2. **Emergency Procurement:**
   - Use Petty Cash (up to ₱15,000)
   - Emergency Purchase Order
   - Regularize within 3 days

**Contact Numbers:**
- Semaphore Support: +63 2 XXXX XXXX
- Finance Officer: +63 9XX XXX XXXX
- IT Admin: +63 9XX XXX XXXX

---

## Summary: Payment Flow

1. **Government allocates budget** → Office operational funds
2. **Finance creates PO** → Based on projected usage
3. **Purchase SMS credits** → Via bank transfer
4. **System tracks usage** → Real-time monitoring
5. **Monthly reconciliation** → Match usage with billing
6. **Process payment** → Within 30 days
7. **File liquidation** → With complete documentation
8. **COA audit** → Annual review

This ensures transparent, compliant, and sustainable funding for the SMS OTP service while maintaining accessibility for all constituents.

---

*Document Version: 1.0*
*Approved by: Finance Department*
*Last Updated: January 2025*
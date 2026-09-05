from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db.models.signals import post_save
from django.dispatch import receiver


phone_validator = RegexValidator(
    regex=r'^\+?\d{9,15}$',
    message="Phone number must contain 9 to 15 digits, optionally starting with '+'."
)

pincode_validator = RegexValidator(
    regex=r'^\d{4,10}$',
    message="Enter a valid pincode/ZIP (4 to 10 digits)."
)


class Profile(models.Model):
    """
    Extends Django's built-in User model with an application role.
    Every user is either a Distributor (manages their own customers)
    or an Admin / Super Admin (can view & manage all customers).
    """
    ROLE_DISTRIBUTOR = 'distributor'
    ROLE_ADMIN = 'admin'
    ROLE_CHOICES = (
        (ROLE_DISTRIBUTOR, 'Distributor'),
        (ROLE_ADMIN, 'Admin / Super Admin'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_DISTRIBUTOR)
    phone = models.CharField(validators=[phone_validator], max_length=17, blank=True)
    company_name = models.CharField(max_length=150, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'profiles'
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

    @property
    def is_admin(self):
        return self.role == self.ROLE_ADMIN

    @property
    def is_distributor(self):
        return self.role == self.ROLE_DISTRIBUTOR


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """Automatically create a Profile (defaulting to Distributor) for every new User."""
    if created:
        Profile.objects.get_or_create(user=instance)
    else:
        Profile.objects.get_or_create(user=instance)


class Customer(models.Model):
    """
    A customer / retailer / sub-dealer record that belongs to exactly one
    Distributor. Admin / Super Admin users can see and manage records
    across every distributor.
    """
    STATUS_ACTIVE = 'active'
    STATUS_INACTIVE = 'inactive'
    STATUS_CHOICES = (
        (STATUS_ACTIVE, 'Active'),
        (STATUS_INACTIVE, 'Inactive'),
    )

    distributor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='customers',
        help_text="The distributor who owns this customer record."
    )
    name = models.CharField(max_length=150)
    email = models.EmailField(blank=True)
    phone = models.CharField(validators=[phone_validator], max_length=17)
    company_name = models.CharField(max_length=150, blank=True)
    address_line = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(validators=[pincode_validator], max_length=10, blank=True)
    gst_number = models.CharField(max_length=20, blank=True, verbose_name="GST / Tax Number")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'customers'
        ordering = ['-created_at']
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['phone']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return self.name

from django.db import models

class Users(models.Model):
    user_name = models.CharField(max_length=30)
    user_mobile = models.CharField(max_length=10)
    user_password = models.CharField(max_length=15)
    user_created_at = models.DateField(auto_now_add=True)
    store_name = models.CharField(max_length=100, null=True, blank=True)
    class Meta:
        verbose_name = "Store User"
        verbose_name_plural = "Store Users"

    def __str__(self):
        return self.user_name
    
class Bills(models.Model):
    customer_name = models.CharField(max_length=20)
    customer_mobile = models.CharField(max_length=10)
    purchase_product = models.IntegerField()
    quantity = models.PositiveIntegerField()
    user = models.ForeignKey(Users, on_delete=models.CASCADE, null=True)
    bill_date = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name = "Sales Bill"
        verbose_name_plural = "Sales Bills"

    def __str__(self):
        return self.customer_name

class Store(models.Model):
    p_id = models.IntegerField()
    p_name = models.CharField(max_length=100)
    p_price = models.IntegerField()
    p_quantity = models.IntegerField(default=100)
    user = models.ForeignKey(Users, on_delete=models.CASCADE, null=True)
    p_list_date = models.DateField(auto_now_add=True)
    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
    def __str__(self):
        return str(self.p_id)
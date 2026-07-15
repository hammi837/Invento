from django.db import models


class ProductForecast(models.Model):
    product_id = models.CharField(max_length=20, db_index=True)
    forecast_date = models.DateField()
    predicted_units = models.FloatField()
    current_stock = models.IntegerField(null=True, blank=True)
    days_until_stockout = models.IntegerField(null=True, blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product_id', 'forecast_date')
        ordering = ['-forecast_date']

    def __str__(self):
        return f"{self.product_id} — {self.forecast_date}: {self.predicted_units:.0f} units"

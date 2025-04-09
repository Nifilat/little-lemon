from rest_framework import serializers
from .models import Category, MenuItem, Cart, Order, OrderItem
from django.contrib.auth.models import User

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'slug', 'title']


class MenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category', 'category_id']


class CartSerializer(serializers.ModelSerializer):
    menuitem = MenuItemSerializer(read_only=True)
    menuitem_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'menuitem', 'menuitem_id', 'quantity', 'unit_price', 'price']
        read_only_fields = ['unit_price', 'price']

    def create(self, validated_data):
        menuitem = MenuItem.objects.get(id=validated_data['menuitem_id'])
        quantity = validated_data['quantity']
        validated_data['unit_price'] = menuitem.price
        validated_data['price'] = quantity * menuitem.price
        validated_data['menuitem'] = menuitem
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class OrderItemSerializer(serializers.ModelSerializer):
    menuitem = MenuItemSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'menuitem', 'quantity', 'unit_price', 'price']


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True, source='orderitem_set')
    user = serializers.StringRelatedField(read_only=True)
    delivery_crew = serializers.StringRelatedField()
    delivery_crew_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Order
        fields = ['id', 'user', 'delivery_crew', 'delivery_crew_id', 'status', 'total', 'date', 'order_items']
        read_only_fields = ['total', 'date']

    def update(self, instance, validated_data):
        if 'delivery_crew_id' in validated_data:
            try:
                crew = User.objects.get(id=validated_data['delivery_crew_id'])
                instance.delivery_crew = crew
            except User.DoesNotExist:
                raise serializers.ValidationError("Invalid delivery crew ID")
        if 'status' in validated_data:
            instance.status = validated_data['status']
        instance.save()
        return instance

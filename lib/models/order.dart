class Order {
  final int orderId;
  final String orderDate;
  final double totalPrice;
  final String status;
  final String shippingAddress;
  final List<OrderItem> items;

  Order({
    required this.orderId,
    required this.orderDate,
    required this.totalPrice,
    required this.status,
    required this.shippingAddress,
    required this.items,
  });

  factory Order.fromJson(Map<String, dynamic> json) {
    return Order(
      orderId: json['order_id'],
      orderDate: json['order_date'],
      totalPrice: json['total_price'].toDouble(),
      status: json['status'],
      shippingAddress: json['shipping_address'] ?? '',
      items: (json['items'] as List)
          .map((item) => OrderItem.fromJson(item))
          .toList(),
    );
  }
}

class OrderItem {
  final int productId;
  final String name;
  final int quantity;
  final double price;
  final String image;

  OrderItem({
    required this.productId,
    required this.name,
    required this.quantity,
    required this.price,
    required this.image,
  });

  factory OrderItem.fromJson(Map<String, dynamic> json) {
    return OrderItem(
      productId: json['product_id'],
      name: json['name'],
      quantity: json['quantity'],
      price: json['price'].toDouble(),
      image: json['image'],
    );
  }
}

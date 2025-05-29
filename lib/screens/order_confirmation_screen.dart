import 'package:flutter/material.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import 'package:lithub_mobile/services/api_service.dart';

class OrderConfirmationScreen extends StatefulWidget {
  final int orderId;

  const OrderConfirmationScreen({Key? key, required this.orderId}) : super(key: key);

  @override
  State<OrderConfirmationScreen> createState() => _OrderConfirmationScreenState();
}

class _OrderConfirmationScreenState extends State<OrderConfirmationScreen> {
  Map<String, dynamic>? order;
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    _fetchOrder();
  }

  Future<void> _fetchOrder() async {
    setState(() => isLoading = true);
    final result = await ApiService.getOrderById(widget.orderId);
    setState(() {
      order = result;
      isLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    if (isLoading) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }
    if (order == null) {
      return const Scaffold(
        body: Center(child: Text('Order not found')),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Order Confirmation', style: TextStyle(color: Colors.white)),
        backgroundColor: Colors.deepPurple,
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Breadcrumb
              Row(
                children: [
                  TextButton(
                    onPressed: () => Navigator.pushNamedAndRemoveUntil(
                      context, '/main', (route) => false),
                    child: const Text('Shop', style: TextStyle(color: Colors.deepPurple)),
                  ),
                  const Text(' > '),
                  TextButton(
                    onPressed: () => Navigator.pushNamed(context, '/orders'),
                    child: const Text('Orders', style: TextStyle(color: Colors.deepPurple)),
                  ),
                  const Text(' > '),
                  const Text('Order Confirmation'),
                ],
              ),
              
              const SizedBox(height: 24),
              
              // Confirmation Header
              Center(
                child: Column(
                  children: [
                    const Text(
                      'Order Confirmation',
                      style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 24),
                    const Icon(
                      FontAwesomeIcons.circleCheck,
                      color: Colors.green,
                      size: 64,
                    ),
                    const SizedBox(height: 16),
                    const Text(
                      'Thank you for your order!',
                      style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Order Number: ${order!['order_id']}',
                      style: const TextStyle(fontSize: 16),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'A confirmation email has been sent to ${order!['email'] ?? "your email"}',
                      style: const TextStyle(fontSize: 16),
                      overflow: TextOverflow.ellipsis,
                      textAlign: TextAlign.center,
                    ),
                  ],
                ),
              ),
              
              const SizedBox(height: 32),
              
              // Order Details
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Shipping Details
                  Expanded(
                    child: Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: Colors.grey[100],
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'Shipping Details',
                            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                          ),
                          const SizedBox(height: 12),
                          Text(order!['shipping_address'] ?? ''),
                        ],
                      ),
                    ),
                  ),
                  
                  const SizedBox(width: 16),
                  
                  // Payment Details
                  Expanded(
                    child: Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: Colors.grey[100],
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'Payment Method',
                            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                          ),
                          const SizedBox(height: 12),
                          Text(
                            _formatPaymentMethod(order!['payment_method'] ?? ''),
                            style: const TextStyle(fontSize: 16),
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
              
              const SizedBox(height: 32),
              
              // Order Summary
              const Text(
                'Order Summary',
                style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 16),
              
              // Order Items Table
              Container(
                decoration: BoxDecoration(
                  border: Border.all(color: Colors.grey.shade300),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Column(
                  children: [
                    // Table Header
                    Container(
                      padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 16),
                      decoration: BoxDecoration(
                        color: Colors.grey.shade100,
                        borderRadius: const BorderRadius.only(
                          topLeft: Radius.circular(7),
                          topRight: Radius.circular(7),
                        ),
                      ),
                      child: const Row(
                        children: [
                          Expanded(flex: 3, child: Text('Product', style: TextStyle(fontWeight: FontWeight.bold))),
                          Expanded(flex: 1, child: Text('Qty', style: TextStyle(fontWeight: FontWeight.bold))),
                          Expanded(flex: 1, child: Text('Price', style: TextStyle(fontWeight: FontWeight.bold))),
                          Expanded(flex: 1, child: Text('Total', style: TextStyle(fontWeight: FontWeight.bold))),
                        ],
                      ),
                    ),
                    
                    // Table Body
                    ...List.generate(
                      (order!['items'] as List).length,
                      (index) {
                        final item = order!['items'][index];
                        final price = double.tryParse(item['price'].toString()) ?? 0.0;
                        final quantity = int.tryParse(item['quantity'].toString()) ?? 0;
                        final total = price * quantity;
                        
                        return Padding(
                          padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 16),
                          child: Row(
                            children: [
                              Expanded(
                                flex: 3,
                                child: Row(
                                  children: [
                                    ClipRRect(
                                      borderRadius: BorderRadius.circular(6),
                                      child: Image.network(
                                        'http://192.168.1.16:5000/static/images/${item['image']}',
                                        width: 40,
                                        height: 40,
                                        fit: BoxFit.cover,
                                        errorBuilder: (context, error, stackTrace) => const Icon(Icons.image_not_supported),
                                      ),
                                    ),
                                    const SizedBox(width: 8),
                                    Expanded(
                                      child: Text(
                                        item['name'] ?? 'Unknown',
                                        overflow: TextOverflow.ellipsis,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                              Expanded(flex: 1, child: Text('$quantity')),
                              Expanded(flex: 1, child: Text('₱${price.toStringAsFixed(2)}')),
                              Expanded(flex: 1, child: Text('₱${total.toStringAsFixed(2)}')),
                            ],
                          ),
                        );
                      },
                    ),
                    
                    // Divider
                    const Divider(height: 1),
                    
                    // Subtotal
                    Padding(
                      padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 16),
                      child: Row(
                        children: [
                          const Expanded(flex: 5, child: Text('Subtotal')),
                          Expanded(
                            flex: 1, 
                            child: Text('₱${(double.tryParse(order!['total_price'].toString()) ?? 0.0).toStringAsFixed(2)}'),
                          ),
                        ],
                      ),
                    ),
                    
                    // Shipping
                    Padding(
                      padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 16),
                      child: Row(
                        children: [
                          const Expanded(flex: 5, child: Text('Shipping')),
                          const Expanded(flex: 1, child: Text('Free')),
                        ],
                      ),
                    ),
                    
                    // Divider
                    const Divider(height: 1),
                    
                    // Total
                    Padding(
                      padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 16),
                      child: Row(
                        children: [
                          const Expanded(
                            flex: 5, 
                            child: Text('Total', style: TextStyle(fontWeight: FontWeight.bold)),
                          ),
                          Expanded(
                            flex: 1, 
                            child: Text(
                              '₱${(double.tryParse(order!['total_price'].toString()) ?? 0.0).toStringAsFixed(2)}',
                              style: const TextStyle(fontWeight: FontWeight.bold),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
              
              const SizedBox(height: 32),
              
              // Action Buttons
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Flexible(
                    child: ElevatedButton(
                      onPressed: () => Navigator.pushNamedAndRemoveUntil(
                        context, '/main', (route) => false),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.deepPurple,
                        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                      ),
                      child: const Text('Continue Shopping', style: TextStyle(color: Colors.white)),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Flexible(
                    child: OutlinedButton(
                      onPressed: () => Navigator.pushNamed(context, '/account/purchases'),
                      style: OutlinedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                      ),
                      child: const Text('View All Orders'),
                    ),
                  ),
                ],
              ),
              
              const SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }
  
  String _formatPaymentMethod(String method) {
    if (method.isEmpty) return '';
    
    // Replace underscores with spaces and capitalize each word
    final words = method.split('_');
    final capitalizedWords = words.map((word) => 
      word.isNotEmpty ? word[0].toUpperCase() + word.substring(1) : ''
    ).toList();
    
    return capitalizedWords.join(' ');
  }
}

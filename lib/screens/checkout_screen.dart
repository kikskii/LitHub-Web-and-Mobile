import 'package:flutter/material.dart';
import 'package:lithub_mobile/services/api_service.dart';
import 'package:lithub_mobile/screens/order_confirmation_screen.dart';

class CheckoutScreen extends StatefulWidget {
  final List<dynamic> selectedItems;
  final double total;

  const CheckoutScreen({super.key, required this.selectedItems, required this.total});

  @override
  State<CheckoutScreen> createState() => _CheckoutScreenState();
}

class _CheckoutScreenState extends State<CheckoutScreen> {
  Map<String, dynamic>? userDetails;
  String? selectedPaymentMethod;
  bool isLoading = true;
  bool showCardFields = false;
  
  // Card details controllers
  final cardNameController = TextEditingController();
  final cardNumberController = TextEditingController();
  final cardExpiryController = TextEditingController();
  final cardCvvController = TextEditingController();

  @override
  void initState() {
    super.initState();
    loadUserDetails();
  }

  @override
  void dispose() {
    cardNameController.dispose();
    cardNumberController.dispose();
    cardExpiryController.dispose();
    cardCvvController.dispose();
    super.dispose();
  }

  Future<void> loadUserDetails() async {
    try {
      print("[Checkout] Loading user details...");
      final user = await ApiService.getUserProfile();
      print("[Checkout] User details received: $user");
      print("[Checkout] Default address: ${user['default_address']}");
      
      if (mounted) {
        setState(() {
          userDetails = user;
          isLoading = false;
        });
      }
    } catch (e) {
      print("[Checkout] Error loading user details: $e");
      if (mounted) {
        setState(() {
          isLoading = false;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to load user details: $e')),
        );
      }
    }
  }

  void _toggleCardFields(String? value) {
    setState(() {
      selectedPaymentMethod = value;
      showCardFields = value == 'credit_card';
    });
  }

  Future<void> submitOrder() async {
    if (selectedPaymentMethod == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Please select a payment method")),
      );
      return;
    }

    // Validate card details if credit card is selected
    if (selectedPaymentMethod == 'credit_card') {
      if (cardNameController.text.isEmpty || 
          cardNumberController.text.isEmpty || 
          cardExpiryController.text.isEmpty || 
          cardCvvController.text.isEmpty) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text("Please fill in all card details")),
        );
        return;
      }
    }
    
    setState(() {
      isLoading = true;
    });
    
    try {
      print("Submitting order with payment method: $selectedPaymentMethod");
      final result = await ApiService.checkout(
        widget.selectedItems,
        widget.total,
        selectedPaymentMethod!,
      );
      
      print("Checkout result: $result");
      
      if (result['success'] == true) {
        // Get order details - handle both response formats
        final int orderId = result['data'] != null && result['data']['order_id'] != null 
            ? result['data']['order_id'] 
            : (result['order_id'] ?? 0);
        
        print("Order created with ID: $orderId");
        
        if (orderId > 0) {
          try {
            final orderDetails = await ApiService.getOrderDetails(orderId);
            print("Order details retrieved: $orderDetails");
            
            if (mounted) {
              setState(() {
                isLoading = false;
              });
              
              // Navigate to order confirmation screen
              Navigator.pushReplacement(
                context,
                MaterialPageRoute(
                  builder: (context) => OrderConfirmationScreen(orderId: orderDetails['order_id']),
                ),
              );
            }
          } catch (e) {
            print("Error getting order details: $e");
            // Even if we can't get order details, still show confirmation
            if (mounted) {
              setState(() {
                isLoading = false;
              });
              
              // Create a minimal order object with just the ID
              final Map<String, dynamic> minimalOrder = {
                'order_id': orderId,
                'total_price': widget.total,
                'payment_method': selectedPaymentMethod,
                'items': widget.selectedItems
              };
              
              Navigator.pushReplacement(
                context,
                MaterialPageRoute(
                  builder: (context) => OrderConfirmationScreen(orderId: minimalOrder['order_id']),
                ),
              );
            }
          }
        } else {
          throw Exception(result['error'] ?? 'Failed to place order');
        }
      } else {
        throw Exception(result['error'] ?? 'Failed to place order');
      }
    } catch (e) {
      print("Error in submitOrder: $e");
      if (mounted) {
        setState(() {
          isLoading = false;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (isLoading) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }

    final address = userDetails?['default_address'];
    
    return Scaffold(
      appBar: AppBar(
        title: const Text('Checkout', style: TextStyle(color: Colors.white)), 
        backgroundColor: Colors.deepPurple,
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Breadcrumb
              Row(
                children: [
                  TextButton(
                    onPressed: () => Navigator.pop(context),
                    child: const Text('Shop', style: TextStyle(color: Colors.deepPurple)),
                  ),
                  const Text(' > '),
                  const Text('Checkout'),
                ],
              ),
              
              const SizedBox(height: 20),
              const Text('Checkout', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
              const SizedBox(height: 20),
              
              // Billing & Shipping Address
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text('Billing & Shipping Address', 
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                  TextButton(
                    onPressed: () {
                      // Navigate to address edit screen
                      Navigator.pushNamed(context, '/address').then((_) => loadUserDetails());
                    },
                    child: const Text('Edit Address', style: TextStyle(color: Colors.deepPurple)),
                  ),
                ],
              ),
              
              const SizedBox(height: 10),
              
              // Address display
              if (address != null)
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.grey[100],
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('${address['first_name']} ${address['last_name']}', 
                        style: const TextStyle(fontWeight: FontWeight.bold)),
                      Text('${address['phone']}'),
                      const SizedBox(height: 8),
                      Text('${address['address']}'),
                      Text('${address['barangay']}, ${address['city']}'),
                      Text('${address['province']}, ${address['country']} ${address['postcode']}'),
                      Text('${address['email']}'),
                      const SizedBox(height: 8),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                        decoration: BoxDecoration(
                          color: Colors.deepPurple.withOpacity(0.2),
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: const Text('Default', 
                          style: TextStyle(color: Colors.deepPurple, fontSize: 12)),
                      ),
                    ],
                  ),
                )
              else
                Container(
                  padding: const EdgeInsets.all(20),
                  alignment: Alignment.center,
                  decoration: BoxDecoration(
                    color: Colors.grey[100],
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Column(
                    children: [
                      const Text('No default address set. Please add an address in your profile.'),
                      const SizedBox(height: 10),
                      ElevatedButton(
                        onPressed: () {
                          Navigator.pushNamed(context, '/address').then((_) => loadUserDetails());
                        },
                        style: ElevatedButton.styleFrom(backgroundColor: Colors.deepPurple),
                        child: const Text('Add Address', style: TextStyle(color: Colors.white)),
                      ),
                    ],
                  ),
                ),
              
              const SizedBox(height: 30),
              
              // Order summary
              const Text('Your Order', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
              const SizedBox(height: 10),
              
              // Order items
              Container(
                decoration: BoxDecoration(
                  border: Border.all(color: Colors.grey.shade300),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Column(
                  children: [
                    // Header
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: Colors.grey.shade100,
                        borderRadius: const BorderRadius.only(
                          topLeft: Radius.circular(7),
                          topRight: Radius.circular(7),
                        ),
                      ),
                      child: const Row(
                        children: [
                          Expanded(flex: 1, child: Text('Image', style: TextStyle(fontWeight: FontWeight.bold))),
                          Expanded(flex: 2, child: Text('Product', style: TextStyle(fontWeight: FontWeight.bold))),
                          Expanded(flex: 1, child: Text('Qty', style: TextStyle(fontWeight: FontWeight.bold))),
                          Expanded(flex: 1, child: Text('Total', style: TextStyle(fontWeight: FontWeight.bold))),
                        ],
                      ),
                    ),
                    
                    // Items
                    ...widget.selectedItems.map((item) => Padding(
                      padding: const EdgeInsets.all(12),
                      child: Row(
                        children: [
                          Expanded(
                            flex: 1,
                            child: _buildProductImage(
                              'http://192.168.1.16:5000/static/images/${item['image']}'
                            ),
                          ),
                          Expanded(
                            flex: 2,
                            child: Text(item['name'] ?? 'Unknown'),
                          ),
                          Expanded(
                            flex: 1,
                            child: Text('${item['quantity'] ?? 1}'),
                          ),
                          Expanded(
                            flex: 1,
                            child: Text('₱${_calculateItemTotal(item)}'),
                          ),
                        ],
                      ),
                    )).toList(),
                  ],
                ),
              ),
              
              const SizedBox(height: 30),
              
              // Order total
              const Text('Order Total', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
              const SizedBox(height: 10),
              
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  border: Border.all(color: Colors.grey.shade300),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Column(
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text('Order Subtotal'),
                        Text('₱${widget.total.toStringAsFixed(2)}'),
                      ],
                    ),
                    const SizedBox(height: 8),
                    const Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text('Shipping'),
                        Text('Free Shipping'),
                      ],
                    ),
                    const Divider(height: 20),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text('Total', style: TextStyle(fontWeight: FontWeight.bold)),
                        Text('₱${widget.total.toStringAsFixed(2)}', 
                          style: const TextStyle(fontWeight: FontWeight.bold)),
                      ],
                    ),
                  ],
                ),
              ),
              
              const SizedBox(height: 30),
              
              // Payment method
              const Text('Payment Method', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
              const SizedBox(height: 10),
              
              // Payment dropdown
              DropdownButtonFormField<String>(
                decoration: InputDecoration(
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                  contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                ),
                value: selectedPaymentMethod,
                hint: const Text("Select Payment Method"),
                items: const [
                  DropdownMenuItem(value: 'cod', child: Text('Cash On Delivery')),
                  DropdownMenuItem(value: 'credit_card', child: Text('Credit Card')),
                  DropdownMenuItem(value: 'paypal', child: Text('Paypal')),
                ],
                onChanged: _toggleCardFields,
              ),
              
              // Credit card fields
              if (showCardFields) ...[
                const SizedBox(height: 20),
                TextField(
                  controller: cardNameController,
                  decoration: InputDecoration(
                    labelText: 'Card Holder Name',
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                  ),
                ),
                const SizedBox(height: 10),
                TextField(
                  controller: cardNumberController,
                  decoration: InputDecoration(
                    labelText: 'Card Number',
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                  ),
                  keyboardType: TextInputType.number,
                  maxLength: 16,
                ),
                const SizedBox(height: 10),
                Row(
                  children: [
                    Expanded(
                      child: TextField(
                        controller: cardExpiryController,
                        decoration: InputDecoration(
                          labelText: 'Expiry (MM/YY)',
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(8),
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: TextField(
                        controller: cardCvvController,
                        decoration: InputDecoration(
                          labelText: 'CVV',
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(8),
                          ),
                        ),
                        keyboardType: TextInputType.number,
                        maxLength: 4,
                      ),
                    ),
                  ],
                ),
              ],
              
              const SizedBox(height: 30),
              
              // Place order button
              SizedBox(
                width: double.infinity,
                height: 50,
                child: ElevatedButton(
                  onPressed: submitOrder,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.deepPurple,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                  ),
                  child: const Text('Place Order Now', 
                    style: TextStyle(color: Colors.white, fontSize: 16)),
                ),
              ),
              
              const SizedBox(height: 30),
            ],
          ),
        ),
      ),
    );
  }
  
  // Helper method to handle image loading with fallback
  Widget _buildProductImage(String? imageUrl) {
    if (imageUrl == null || imageUrl.isEmpty) {
      // Use a local asset as placeholder instead of network image
      return Container(
        height: 50,
        width: 50,
        color: Colors.grey[300],
        child: const Icon(Icons.image, color: Colors.grey),
      );
    }
    
    return Image.network(
      imageUrl,
      height: 50,
      width: 50,
      fit: BoxFit.cover,
      errorBuilder: (context, error, stackTrace) {
        // On error, show a placeholder
        return Container(
          height: 50,
          width: 50,
          color: Colors.grey[300],
          child: const Icon(Icons.broken_image, color: Colors.grey),
        );
      },
    );
  }

  // Helper method to calculate item total with proper type handling
  String _calculateItemTotal(Map<String, dynamic> item) {
    // Get price and quantity, ensuring they are numeric
    double price = 0.0;
    int quantity = 1;
    
    // Handle price - could be String or numeric
    if (item['price'] != null) {
      if (item['price'] is String) {
        price = double.tryParse(item['price']) ?? 0.0;
      } else {
        price = (item['price'] as num).toDouble();
      }
    }
    
    // Handle quantity - could be String or numeric
    if (item['quantity'] != null) {
      if (item['quantity'] is String) {
        quantity = int.tryParse(item['quantity']) ?? 1;
      } else {
        quantity = (item['quantity'] as num).toInt();
      }
    }
    
    // Calculate and format total
    return (price * quantity).toStringAsFixed(2);
  }
}

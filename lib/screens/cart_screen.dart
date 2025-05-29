import 'package:flutter/material.dart';
import 'package:lithub_mobile/services/api_service.dart';
import 'package:lithub_mobile/screens/checkout_screen.dart';

class CartScreen extends StatefulWidget {
  @override
  _CartScreenState createState() => _CartScreenState();
}

class _CartScreenState extends State<CartScreen> {
  List<dynamic> cartItems = [];
  Set<int> selectedItemIds = {};
  double total = 0.0;
  bool selectAll = false;

  @override
  void initState() {
    super.initState();
    fetchCartItems();
  }

  Future<void> fetchCartItems() async {
    final items = await ApiService.getCart();
    setState(() {
      cartItems = items;
      selectedItemIds = items.map((e) => e['product_id'] as int).toSet();
      selectAll = true;
      total = calculateTotal();
    });
  }

  double calculateTotal() {
    return cartItems.fold(0.0, (sum, item) {
      if (selectedItemIds.contains(item['product_id'])) {
        final price = double.tryParse(item['price'].toString()) ?? 0.0;
        final qty = int.tryParse(item['quantity'].toString()) ?? 1;
        return sum + price * qty;
      }
      return sum;
    });
  }

  Future<void> updateQuantityBackend(int productId, int newQuantity) async {
    await ApiService.updateCartQuantity(productId, newQuantity); // You already support this
  }

  void updateQuantity(int index, int newQuantity) async {
    final productId = cartItems[index]['product_id'];
    setState(() => cartItems[index]['quantity'] = newQuantity);
    await updateQuantityBackend(productId, newQuantity);
    setState(() => total = calculateTotal());
  }

  Future<bool?> confirmRemove(int index) async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Remove Item'),
        content: const Text('Are you sure you want to remove this item from the cart?'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Cancel')),
          TextButton(onPressed: () => Navigator.pop(context, true), child: const Text('Remove')),
        ],
      ),
    );

    if (confirm == true) {
      final productId = cartItems[index]['product_id'];
      await ApiService.removeFromCart(productId);
      setState(() {
        cartItems.removeAt(index);
        selectedItemIds.remove(productId);
        selectAll = selectedItemIds.length == cartItems.length;
        total = calculateTotal();
      });
      return true;
    }
    return false;
  }

  void toggleSelectAll(bool? value) {
    setState(() {
      selectAll = value ?? false;
      selectedItemIds = selectAll ? cartItems.map((e) => e['product_id'] as int).toSet() : {};
      total = calculateTotal();
    });
  }

  Future<void> showCheckoutDialog() async {
    if (selectedItemIds.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select items to checkout.')),
      );
      return;
    }

    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Confirm Checkout'),
        content: Text('Proceed to checkout ₱${total.toStringAsFixed(2)} for selected items?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: Colors.deepPurple),
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Continue', style: TextStyle(color: Colors.white)),
          ),
        ],
      ),
    );

    if (confirmed == true) {
      final selectedItems = cartItems
          .where((item) => selectedItemIds.contains(item['product_id']))
          .toList();

      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (_) => CheckoutScreen(
            selectedItems: selectedItems,
            total: total,
          ),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('My Cart', style: TextStyle(color: Colors.white)),
        backgroundColor: Colors.deepPurple,
      ),
      body: Column(
        children: [
          CheckboxListTile(
            title: const Text('Select All'),
            value: selectAll,
            onChanged: toggleSelectAll,
            controlAffinity: ListTileControlAffinity.leading,
          ),
          Expanded(
            child: cartItems.isEmpty
                ? Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.favorite_border, size: 64, color: Colors.grey[400]),
                        const SizedBox(height: 16),
                        Text(
                          'No items in the cart',
                          style: TextStyle(
                            fontSize: 16,
                            color: Colors.grey[600],
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ],
                    ),
                  )
                : ListView.builder(
                    padding: const EdgeInsets.all(10),
                    itemCount: cartItems.length,
                    itemBuilder: (context, index) {
                      final item = cartItems[index];
                      final productId = item['product_id'];
                      final price = double.tryParse(item['price'].toString()) ?? 0.0;
                      final quantity = int.tryParse(item['quantity'].toString()) ?? 1;

                      return Dismissible(
                        key: Key(productId.toString()),
                        direction: DismissDirection.endToStart,
                        background: Container(
                          alignment: Alignment.centerRight,
                          padding: const EdgeInsets.symmetric(horizontal: 20),
                          color: Colors.red,
                          child: const Icon(Icons.delete, color: Colors.white),
                        ),
                        confirmDismiss: (_) => confirmRemove(index),
                        child: Card(
                          margin: const EdgeInsets.symmetric(vertical: 6),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                          child: CheckboxListTile(
                            value: selectedItemIds.contains(productId),
                            onChanged: (value) {
                              setState(() {
                                if (value == true) {
                                  selectedItemIds.add(productId);
                                } else {
                                  selectedItemIds.remove(productId);
                                }
                                selectAll = selectedItemIds.length == cartItems.length;
                                total = calculateTotal();
                              });
                            },
                            controlAffinity: ListTileControlAffinity.leading,
                            title: Row(
                              children: [
                                ClipRRect(
                                  borderRadius: BorderRadius.circular(8),
                                  child: Image.network(
                                    'http://192.168.1.16:5000/static/images/${item['image']}',
                                    width: 60,
                                    height: 60,
                                    fit: BoxFit.cover,
                                  ),
                                ),
                                const SizedBox(width: 10),
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Text(item['name'], style: const TextStyle(fontWeight: FontWeight.bold)),
                                      const SizedBox(height: 4),
                                      Text('₱${price.toStringAsFixed(2)}'),
                                      Row(
                                        children: [
                                          IconButton(
                                            icon: const Icon(Icons.remove),
                                            onPressed: quantity > 1
                                                ? () => updateQuantity(index, quantity - 1)
                                                : null,
                                          ),
                                          Text('$quantity'),
                                          IconButton(
                                            icon: const Icon(Icons.add),
                                            onPressed: () => updateQuantity(index, quantity + 1),
                                          ),
                                        ],
                                      ),
                                    ],
                                  ),
                                ),
                                Text('₱${(price * quantity).toStringAsFixed(2)}',
                                    style: const TextStyle(fontWeight: FontWeight.w600)),
                              ],
                            ),
                          ),
                        ),
                      );
                    },
                  ),
          ),
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                Text('Total: ₱${total.toStringAsFixed(2)}',
                    style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
                const SizedBox(height: 10),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: selectedItemIds.isEmpty ? null : showCheckoutDialog,
                    style: ElevatedButton.styleFrom(backgroundColor: Colors.deepPurple),
                    child: const Text('Proceed to Checkout', style: TextStyle(color: Colors.white)),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

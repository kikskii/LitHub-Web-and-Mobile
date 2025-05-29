import 'package:flutter/material.dart';
import 'package:lithub_mobile/services/api_service.dart';
import 'package:lithub_mobile/screens/order_confirmation_screen.dart';

class AccountPurchaseScreen extends StatefulWidget {
  const AccountPurchaseScreen({Key? key}) : super(key: key);

  @override
  State<AccountPurchaseScreen> createState() => _AccountPurchaseScreenState();
}

class _AccountPurchaseScreenState extends State<AccountPurchaseScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  List<dynamic> orders = [];
  bool isLoading = true;
  String? error;
  TextEditingController searchController = TextEditingController();
  
  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 6, vsync: this);
    _fetchOrders();
    
    _tabController.addListener(() {
      if (!_tabController.indexIsChanging) {
        _fetchOrdersByStatus(_getStatusFromIndex(_tabController.index));
      }
    });
  }
  
  @override
  void dispose() {
    _tabController.dispose();
    searchController.dispose();
    super.dispose();
  }
  
  String _getStatusFromIndex(int index) {
    switch (index) {
      case 0: return 'all';
      case 1: return 'pending';
      case 2: return 'processing';
      case 3: return 'shipped';
      case 4: return 'completed';
      case 5: return 'cancelled';
      default: return 'all';
    }
  }
  
  Future<void> _fetchOrders() async {
    setState(() {
      isLoading = true;
      error = null;
    });
    
    try {
      final result = await ApiService.getUserOrders();
      setState(() {
        orders = result;
        isLoading = false;
      });
    } catch (e) {
      setState(() {
        error = e.toString();
        isLoading = false;
      });
    }
  }
  
  Future<void> _fetchOrdersByStatus(String status) async {
    setState(() {
      isLoading = true;
      error = null;
    });
    
    try {
      final result = await ApiService.getUserOrders(status: status);
      setState(() {
        orders = result;
        isLoading = false;
      });
    } catch (e) {
      setState(() {
        error = e.toString();
        isLoading = false;
      });
    }
  }
  
  Future<void> _searchOrders(String query) async {
    if (query.isEmpty) {
      _fetchOrdersByStatus(_getStatusFromIndex(_tabController.index));
      return;
    }
    
    setState(() {
      isLoading = true;
      error = null;
    });
    
    try {
      final result = await ApiService.searchUserOrders(query);
      setState(() {
        orders = result;
        isLoading = false;
      });
    } catch (e) {
      setState(() {
        error = e.toString();
        isLoading = false;
      });
    }
  }
  
  Future<void> _showOrderReceivedModal(int orderId) async {
    final result = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: Colors.purple.withOpacity(0.1),
                shape: BoxShape.circle,
              ),
              child: const Icon(Icons.inventory_2, color: Colors.deepPurple),
            ),
            const SizedBox(width: 16),
            const Text('Confirm Order Receipt'),
          ],
        ),
        content: const Text(
          'Have you received your order in good condition? This action cannot be undone.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context, true),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.deepPurple,
            ),
            child: const Text('Confirm Receipt'),
          ),
        ],
      ),
    );
    
    if (result == true) {
      try {
        await ApiService.updateOrderStatus(orderId, 'completed');
        _fetchOrdersByStatus(_getStatusFromIndex(_tabController.index));
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Order marked as received')),
          );
        }
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Error: $e')),
          );
        }
      }
    }
  }
  
  Future<void> _showRatingModal(int productId, String productName, String productImage) async {
    int rating = 0;
    String comment = '';
    
    final result = await showDialog<Map<String, dynamic>>(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setState) => AlertDialog(
          title: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.amber.withOpacity(0.1),
                  shape: BoxShape.circle,
                ),
                child: const Icon(Icons.star, color: Colors.amber),
              ),
              const SizedBox(width: 16),
              const Text('Rate Product'),
            ],
          ),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    CircleAvatar(
                      radius: 30,
                      backgroundImage: NetworkImage('${ApiService.baseUrl}/static/images/$productImage'),
                      onBackgroundImageError: (_, __) => const Icon(Icons.error),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Text(
                        productName,
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 24),
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: List.generate(5, (index) {
                    return IconButton(
                      icon: Icon(
                        index < rating ? Icons.star : Icons.star_border,
                        color: Colors.amber,
                        size: 36,
                      ),
                      onPressed: () {
                        setState(() {
                          rating = index + 1;
                        });
                      },
                    );
                  }),
                ),
                const SizedBox(height: 16),
                TextField(
                  decoration: const InputDecoration(
                    hintText: 'Write your review (optional)',
                    border: OutlineInputBorder(),
                  ),
                  maxLines: 3,
                  onChanged: (value) {
                    comment = value;
                  },
                ),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Cancel'),
            ),
            ElevatedButton(
              onPressed: rating > 0
                  ? () => Navigator.pop(context, {
                        'rating': rating,
                        'comment': comment,
                        'product_id': productId,
                      })
                  : null,
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.deepPurple,
              ),
              child: const Text('Submit Rating'),
            ),
          ],
        ),
      ),
    );
    
    if (result != null) {
      try {
        await ApiService.submitRating(result);
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Rating submitted successfully')),
          );
        }
        _fetchOrdersByStatus(_getStatusFromIndex(_tabController.index));
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Error: $e')),
          );
        }
      }
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('My Purchases'),
        backgroundColor: Colors.deepPurple,
        foregroundColor: Colors.white,
        bottom: TabBar(
          controller: _tabController,
          isScrollable: true,
          labelColor: Colors.white,
          unselectedLabelColor: Colors.white70,
          indicatorColor: Colors.white,
          tabs: const [
            Tab(text: 'All'),
            Tab(text: 'To Pay'),
            Tab(text: 'To Ship'),
            Tab(text: 'To Receive'),
            Tab(text: 'Completed'),
            Tab(text: 'Cancelled'),
          ],
        ),
      ),
      body: Column(
        children: [
          // Search bar
          Container(
            padding: const EdgeInsets.all(16),
            color: Colors.grey[100],
            child: Container(
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(8),
                boxShadow: [
                  BoxShadow(
                    color: Colors.grey.withOpacity(0.1),
                    spreadRadius: 1,
                    blurRadius: 2,
                    offset: const Offset(0, 1),
                  ),
                ],
              ),
              child: TextField(
                controller: searchController,
                decoration: InputDecoration(
                  hintText: 'Search by order number or product',
                  prefixIcon: const Icon(Icons.search, color: Colors.grey),
                  border: InputBorder.none,
                  contentPadding: const EdgeInsets.symmetric(vertical: 12),
                  suffixIcon: IconButton(
                    icon: const Icon(Icons.clear, color: Colors.grey),
                    onPressed: () {
                      searchController.clear();
                      _fetchOrdersByStatus(_getStatusFromIndex(_tabController.index));
                    },
                  ),
                ),
                onSubmitted: _searchOrders,
              ),
            ),
          ),
          
          // Orders list
          Expanded(
            child: isLoading
                ? const Center(child: CircularProgressIndicator())
                : error != null
                    ? Center(child: Text('Error: $error'))
                    : orders.isEmpty
                        ? const Center(child: Text('No orders found'))
                        : ListView.builder(
                            padding: const EdgeInsets.all(16),
                            itemCount: orders.length,
                            itemBuilder: (context, index) {
                              final order = orders[index];
                              return _buildOrderCard(order);
                            },
                          ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildOrderCard(Map<String, dynamic> order) {
    // Use the correct key: 'items'
    final List<Map<String, dynamic>> orderItems = (order['items'] as List?)
        ?.map((item) => Map<String, dynamic>.from(item))
        .toList() ?? [];

    final orderStatus = order['status'] ?? 'pending';
    
    // Fix for date parsing error
    DateTime orderDate;
    try {
      orderDate = DateTime.parse(order['order_date'] ?? DateTime.now().toString());
    } catch (e) {
      // Fallback if date parsing fails
      orderDate = DateTime.now();
    }
    
    final formattedDate = '${orderDate.day}/${orderDate.month}/${orderDate.year}';
    
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Order header
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              border: Border(bottom: BorderSide(color: Colors.grey.shade200)),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  children: [
                    const Icon(Icons.store, color: Colors.deepPurple),
                    const SizedBox(width: 8),
                    Text(
                      'Order #${order['order_id']}',
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 16,
                      ),
                    ),
                  ],
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: _getStatusColor(orderStatus).withOpacity(0.1),
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    _getStatusText(orderStatus),
                    style: TextStyle(
                      color: _getStatusColor(orderStatus),
                      fontWeight: FontWeight.w500,
                      fontSize: 12,
                    ),
                  ),
                ),
              ],
            ),
          ),
          
          // Order date
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            child: Text(
              'Ordered on $formattedDate',
              style: TextStyle(
                color: Colors.grey.shade600,
                fontSize: 14,
              ),
            ),
          ),
          
          // Order items
          if (orderItems.isEmpty)
            Padding(
              padding: const EdgeInsets.all(16),
              child: Text(
                'No items found for this order.',
                style: TextStyle(color: Colors.grey.shade600),
              ),
            )
          else
            ListView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: orderItems.length,
              itemBuilder: (context, index) {
                final item = orderItems[index];
                return Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    border: Border(
                      top: BorderSide(color: Colors.grey.shade200),
                      bottom: index == orderItems.length - 1
                          ? BorderSide.none
                          : BorderSide(color: Colors.grey.shade200),
                    ),
                  ),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Product image
                      ClipRRect(
                        borderRadius: BorderRadius.circular(8),
                        child: Image.network(
                          '${ApiService.baseUrl}/static/images/${item['image'] ?? ''}',
                          width: 80,
                          height: 80,
                          fit: BoxFit.cover,
                          errorBuilder: (context, error, stackTrace) {
                            return Container(
                              width: 80,
                              height: 80,
                              color: Colors.grey.shade300,
                              child: const Icon(Icons.image_not_supported),
                            );
                          },
                        ),
                      ),
                      const SizedBox(width: 16),
                      
                      // Product details
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              item['name'] ?? 'Unknown Product',
                              style: const TextStyle(
                                fontWeight: FontWeight.w500,
                                fontSize: 16,
                              ),
                              maxLines: 2,
                              overflow: TextOverflow.ellipsis,
                            ),
                            const SizedBox(height: 8),
                            Text(
                              '₱${double.tryParse(item['price']?.toString() ?? '0')?.toStringAsFixed(2) ?? '0.00'} x ${item['quantity'] ?? 1}',
                              style: TextStyle(
                                color: Colors.grey.shade700,
                              ),
                            ),
                            const SizedBox(height: 8),
                            if (orderStatus == 'completed' && (item['is_rated'] == 0 || item['is_rated'] == '0'))
                              ElevatedButton(
                                onPressed: () => _showRatingModal(
                                  int.parse(item['product_id'].toString()),
                                  item['name'] ?? '',
                                  item['image'] ?? '',
                                ),
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: Colors.red,
                                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                                  minimumSize: Size.zero,
                                  tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                                ),
                                child: const Text(
                                  'Rate',
                                  style: TextStyle(color: Colors.white),
                                ),
                              )
                            else if (orderStatus == 'completed' && (item['is_rated'] == 1 || item['is_rated'] == '1'))
                              Row(
                                children: [
                                  const Icon(Icons.check_circle, color: Colors.green, size: 16),
                                  const SizedBox(width: 4),
                                  Text(
                                    'Rated',
                                    style: TextStyle(
                                      color: Colors.green.shade700,
                                      fontSize: 14,
                                    ),
                                  ),
                                ],
                              ),
                          ],
                        ),
                      ),
                    ],
                  ),
                );
              },
            ),
          
          // Order footer
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              border: Border(top: BorderSide(color: Colors.grey.shade200)),
              color: Colors.grey.shade50,
            ),
            child: Column(
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      'Order Total:',
                      style: TextStyle(color: Colors.grey.shade700),
                    ),
                    Text(
                      '₱${double.parse(order['total_price']?.toString() ?? '0').toStringAsFixed(2)}',
                      style: const TextStyle(
                        color: Colors.red,
                        fontWeight: FontWeight.bold,
                        fontSize: 16,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                Row(
                  mainAxisAlignment: MainAxisAlignment.end,
                  children: [
                    OutlinedButton(
                      onPressed: () {
                        // Contact seller logic
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(content: Text('Contact seller feature coming soon')),
                        );
                      },
                      style: OutlinedButton.styleFrom(
                        side: BorderSide(color: Colors.grey.shade300),
                      ),
                      child: const Text('Contact Seller'),
                    ),
                    const SizedBox(width: 12),
                    if (orderStatus == 'completed')
                      ElevatedButton(
                        onPressed: () {
                          // Buy again logic
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('Buy again feature coming soon')),
                          );
                        },
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.deepPurple,
                        ),
                        child: const Text('Buy Again', style: TextStyle(color: Colors.white, fontSize: 16)),
                      )
                    else if (orderStatus == 'shipped')
                      ElevatedButton(
                        onPressed: () => _showOrderReceivedModal(int.parse(order['order_id'].toString())),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.red,
                        ),
                        child: const Text('Order Received'),
                      )
                    else
                      OutlinedButton(
                        onPressed: () {
                          // View order details
                          Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (context) => OrderConfirmationScreen(orderId: order['order_id']),
                            ),
                          );
                        },
                        child: const Text('View Details'),
                      ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
  
  Color _getStatusColor(String status) {
    switch (status.toLowerCase()) {
      case 'pending':
        return Colors.orange;
      case 'processing':
        return Colors.blue;
      case 'shipped':
        return Colors.purple;
      case 'completed':
        return Colors.green;
      case 'cancelled':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }
  
  String _getStatusText(String status) {
    switch (status.toLowerCase()) {
      case 'pending':
        return 'To Pay';
      case 'processing':
        return 'To Ship';
      case 'shipped':
        return 'To Receive';
      case 'completed':
        return 'Completed';
      case 'cancelled':
        return 'Cancelled';
      default:
        return status;
    }
  }
}
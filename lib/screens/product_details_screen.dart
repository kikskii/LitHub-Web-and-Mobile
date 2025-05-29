import 'package:flutter/material.dart';
import 'package:lithub_mobile/services/api_service.dart';

class ProductDetailsScreen extends StatefulWidget {
  final int productId;

  const ProductDetailsScreen({Key? key, required this.productId}) : super(key: key);

  @override
  State<ProductDetailsScreen> createState() => _ProductDetailsScreenState();
}

class _ProductDetailsScreenState extends State<ProductDetailsScreen> {
  Map<String, dynamic>? product;
  bool isLoading = true;
  int selectedQuantity = 1;

  @override
  void initState() {
    super.initState();
    _loadProductDetails();
  }

  Future<void> _loadProductDetails() async {
    final details = await ApiService.getProductDetails(widget.productId);
    if (mounted) {
      setState(() {
        product = details;
        isLoading = false;
      });
    }
  }

  Widget _buildStars(double rating, {double size = 24}) {
    int fullStars = rating.floor();
    bool halfStar = (rating - fullStars) >= 0.5;
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: List.generate(5, (index) {
        if (index < fullStars) return Icon(Icons.star, color: Colors.amber, size: size);
        if (index == fullStars && halfStar) return Icon(Icons.star_half, color: Colors.amber, size: size);
        return Icon(Icons.star_border, color: Colors.amber, size: size);
      }),
    );
  }

  @override
  Widget build(BuildContext context) {
    if (isLoading) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }

    if (product == null) {
      return const Scaffold(
        body: Center(child: Text('Product not found.')),
      );
    }

    final List reviews = product!['reviews'] ?? [];
    double avgRating = double.tryParse(product!['average_rating']?.toString() ?? '') ?? 0.0;

    // If avgRating is 0 but there are reviews, calculate the average from reviews
    if ((avgRating == 0.0 || avgRating.isNaN) && reviews.isNotEmpty) {
      double sum = 0.0;
      int count = 0;
      for (var review in reviews) {
        final r = double.tryParse(review['avg_rating']?.toString() ?? '') ?? 0.0;
        if (r > 0) {
          sum += r;
          count++;
        }
      }
      if (count > 0) {
        avgRating = sum / count;
      }
    }

    final int stock = product!['quantity'] ?? 0;
    final int reviewsCount = product!['reviews_count'] ?? (product!['reviews']?.length ?? 0);

    return Scaffold(
      backgroundColor: const Color(0xFFF6F6F6),
      appBar: AppBar(
        title: Text(product!['name'], style: const TextStyle(color: Colors.white)),
        backgroundColor: Colors.deepPurple,
        elevation: 0,
      ),
      body: ListView(
        padding: const EdgeInsets.all(0),
        children: [
          // Hero Product Image
          Container(
            margin: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(20),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.08),
                  blurRadius: 20,
                  offset: const Offset(0, 8),
                ),
              ],
            ),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(20),
              child: Image.network(
                'http://192.168.1.16:5000/static/images/${product!['image']}',
                height: 250,
                width: double.infinity,
                fit: BoxFit.cover,
              ),
            ),
          ),

          // Product Info Card
          Card(
            margin: const EdgeInsets.symmetric(horizontal: 20),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
            elevation: 2,
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Name & Price
                  Text(product!['name'], style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 8),
                  Text("₱${product!['price']}", style: const TextStyle(fontSize: 22, color: Colors.deepPurple, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 12),

                  // Rating & Review Count
                  Row(
                    children: [
                      _buildStars(avgRating, size: 28),
                      const SizedBox(width: 10),
                      Text("($reviewsCount reviews)", style: const TextStyle(color: Colors.grey, fontSize: 16)),
                    ],
                  ),
                  const SizedBox(height: 16),

                  // Author, Genre, Seller, Stock
                  Row(
                    children: [
                      const Icon(Icons.person, size: 18, color: Colors.deepPurple),
                      const SizedBox(width: 6),
                      Text('Author: ${product!['author'] ?? "Unknown"}'),
                    ],
                  ),
                  const SizedBox(height: 6),
                  Row(
                    children: [
                      const Icon(Icons.category, size: 18, color: Colors.deepPurple),
                      const SizedBox(width: 6),
                      Text('Genre: ${product!['genre'] ?? "N/A"}'),
                    ],
                  ),
                  const SizedBox(height: 6),
                  Row(
                    children: [
                      CircleAvatar(
                        radius: 12,
                        backgroundColor: Colors.deepPurple.shade100,
                        child: const Icon(Icons.store, size: 16, color: Colors.deepPurple),
                      ),
                      const SizedBox(width: 6),
                      Text('Seller: ${product!['seller_name'] ?? "Unknown"}'),
                    ],
                  ),
                  const SizedBox(height: 6),
                  Row(
                    children: [
                      const Icon(Icons.inventory_2, size: 18, color: Colors.deepPurple),
                      const SizedBox(width: 6),
                      Text('Available: $stock in stock'),
                    ],
                  ),
                  const SizedBox(height: 18),

                  // Description
                  const Text('Description:', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                  const SizedBox(height: 4),
                  Text(product!['description'] ?? 'No description available.'),
                ],
              ),
            ),
          ),

          // Quantity Selector & Buttons
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text('Quantity:', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                Row(
                  children: [
                    IconButton(
                      icon: const Icon(Icons.remove_circle, color: Colors.deepPurple),
                      onPressed: selectedQuantity > 1
                          ? () => setState(() => selectedQuantity--)
                          : null,
                    ),
                    Text('$selectedQuantity', style: const TextStyle(fontSize: 16)),
                    IconButton(
                      icon: const Icon(Icons.add_circle, color: Colors.deepPurple),
                      onPressed: selectedQuantity < stock
                          ? () => setState(() => selectedQuantity++)
                          : null,
                    ),
                  ],
                ),
              ],
            ),
          ),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 20),
            child: Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: stock > 0 ? () {
                      ApiService.addToCart(product!['product_id'], selectedQuantity);
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text('Added to cart!')),
                      );
                    } : null,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.deepPurple,
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                    ),
                    icon: const Icon(Icons.shopping_cart, color: Colors.white),
                    label: const Text('Add to Cart', style: TextStyle(color: Colors.white, fontSize: 16)),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: stock > 0 ? () {
                      ApiService.checkout(product!['product_id'], selectedQuantity.toDouble(), product!['price'].toString());
                    } : null,
                    style: OutlinedButton.styleFrom(
                      side: const BorderSide(color: Colors.deepPurple, width: 2),
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                    ),
                    icon: const Icon(Icons.flash_on, color: Colors.deepPurple),
                    label: const Text('Buy Now', style: TextStyle(color: Colors.deepPurple, fontSize: 16)),
                  ),
                ),
              ],
            ),
          ),

          // Reviews Section
          const SizedBox(height: 30),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 20),
            child: Text('Reviews', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Colors.deepPurple.shade700)),
          ),
          const SizedBox(height: 10),

          if ((product!['reviews'] as List).isEmpty)
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20),
              child: Text('No reviews yet.', style: TextStyle(color: Colors.grey.shade600)),
            )
          else
            ...product!['reviews'].map<Widget>((review) {
              final double rating = double.tryParse(review['avg_rating'].toString()) ?? 0.0;
              return Card(
                margin: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                elevation: 1,
                color: Colors.white,
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      CircleAvatar(
                        radius: 26,
                        backgroundImage: review['profile_picture'] != null
                            ? NetworkImage('http://192.168.1.16:5000/static/images/profile/${review['profile_picture']}')
                            : const AssetImage('assets/default_avatar.png') as ImageProvider,
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(review['name'], style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                            const SizedBox(height: 4),
                            _buildStars(rating, size: 20),
                            const SizedBox(height: 6),
                            if (review['quality_comment'] != null && review['quality_comment'].toString().isNotEmpty)
                              Text("Product: ${review['quality_comment']}", style: const TextStyle(fontSize: 14)),
                            if (review['service_comment'] != null && review['service_comment'].toString().isNotEmpty)
                              Text("Seller: ${review['service_comment']}", style: const TextStyle(fontSize: 14)),
                            if (review['delivery_comment'] != null && review['delivery_comment'].toString().isNotEmpty)
                              Text("Delivery: ${review['delivery_comment']}", style: const TextStyle(fontSize: 14)),
                            const SizedBox(height: 6),
                            Text(review['review_date'] ?? '', style: const TextStyle(color: Colors.grey, fontSize: 12)),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              );
            }).toList(),
          const SizedBox(height: 30),
        ],
      ),
    );
  }
}
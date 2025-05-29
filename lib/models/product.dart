class Product {
  final int productId;
  final String name;
  final String description;
  final double price;
  final String image;
  final double averageRating;
  final int reviewsCount;
  final bool isFavorite;

  Product({
    required this.productId,
    required this.name,
    required this.description,
    required this.price,
    required this.image,
    required this.averageRating,
    required this.reviewsCount,
    required this.isFavorite,
  });

  factory Product.fromJson(Map<String, dynamic> json) {
    return Product(
      productId: json['product_id'],
      name: json['name'],
      description: json['description'] ?? '',
      price: (json['price'] as num).toDouble(),
      image: json['image'],
      averageRating: (json['average_rating'] as num).toDouble(),
      reviewsCount: json['reviews_count'] ?? 0,
      isFavorite: json['is_favorite'] ?? false,
    );
  }
}

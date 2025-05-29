import 'package:flutter/material.dart';
import 'package:lithub_mobile/services/api_service.dart';

class RecommendedSlider extends StatefulWidget {
  const RecommendedSlider({super.key});

  @override
  State<RecommendedSlider> createState() => _RecommendedSliderState();
}

class _RecommendedSliderState extends State<RecommendedSlider> {
  List<dynamic> books = [];

  @override
  void initState() {
    super.initState();
    _loadRecommendations();
  }

  Future<void> _loadRecommendations() async {
    final data = await ApiService.getProducts(); // or getRecommended()
    setState(() => books = data.take(5).toList());
  }
@override
Widget build(BuildContext context) {
  if (books.isEmpty) {
    return const Padding(
      padding: EdgeInsets.all(20),
      child: Text('No recommendations available at the moment.'),
    );
  }

  return Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      const Padding(
        padding: EdgeInsets.symmetric(horizontal: 20),
        child: Text('Recommend For You', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
      ),
      const SizedBox(height: 4),
      const Padding(
        padding: EdgeInsets.symmetric(horizontal: 20),
        child: Text(
          'Based on your preferences, these selections are curated for you.',
          style: TextStyle(color: Colors.grey, fontSize: 12),
        ),
      ),
      const SizedBox(height: 12),
      SizedBox(
        height: 190,
        child: ListView.builder(
          scrollDirection: Axis.horizontal,
          padding: const EdgeInsets.symmetric(horizontal: 16),
          itemCount: books.length,
          itemBuilder: (context, index) {
            final book = books[index];
            return Padding(
              padding: const EdgeInsets.only(right: 10),
              child: ClipRRect(
                borderRadius: BorderRadius.circular(8),
                child: Image.network(
                  'http://192.168.1.16:5000/static/images/${book['image']}',
                  width: 120,
                  fit: BoxFit.cover,
                  errorBuilder: (context, error, stackTrace) => const Icon(Icons.broken_image),
                ),
              ),
            );
          },
        ),
      ),
    ],
  );
}
}
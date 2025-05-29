import 'package:flutter/material.dart';

class FeatureIconsRow extends StatelessWidget {
  const FeatureIconsRow({super.key});

  @override
  Widget build(BuildContext context) {
    final List<Map<String, dynamic>> features = [
      {'icon': Icons.flash_on, 'label': 'Quick Delivery'},
      {'icon': Icons.security, 'label': 'Secure Payment'},
      {'icon': Icons.thumb_up, 'label': 'Best Quality'},
      {'icon': Icons.star, 'label': 'Return Guarantee'},
    ];

    return SizedBox(
      height: 80,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 16),
        itemCount: features.length,
        separatorBuilder: (_, __) => const SizedBox(width: 20),
        itemBuilder: (context, index) {
          final feature = features[index];
          return Column(
            children: [
              CircleAvatar(
                backgroundColor: Colors.deepPurple.shade50,
                child: Icon(feature['icon'] as IconData, color: Colors.deepPurple),
              ),
              const SizedBox(height: 4),
              Text(
                feature['label'] as String,
                style: const TextStyle(fontSize: 12),
                textAlign: TextAlign.center,
              ),
            ],
          );
        },
      ),
    );
  }
}

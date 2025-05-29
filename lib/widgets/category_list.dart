import 'package:flutter/material.dart';

class CategoryList extends StatelessWidget {
  final List<Map<String, String>> categories = [
    {'label': 'Books', 'value': 'Fiction & Non-Fiction Books'},
    {'label': 'Magazines', 'value': 'Magazines & Periodicals'},
    {'label': 'Music', 'value': 'Music CDs & Vinyl Records'},
    {'label': 'Movies', 'value': 'Movie DVDs & Blu-ray'},
    {'label': 'Games', 'value': 'Video Games & Consoles'},
    {'label': 'Education', 'value': 'Educational DVDs'},
  ];

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 40,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 16),
        separatorBuilder: (_, __) => const SizedBox(width: 10),
        itemCount: categories.length,
        itemBuilder: (context, index) {
          final category = categories[index];
          return GestureDetector(
            onTap: () {
              Navigator.pushNamed(
                context,
                '/category',
                arguments: {
                  'label': category['label'],
                  'value': category['value'],
                },
              );
            },
            child: Chip(
              label: Text(category['label']!),
              backgroundColor: Colors.deepPurple.shade50,
              labelStyle: const TextStyle(color: Colors.deepPurple),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(20),
              ),
            ),
          );
        },
      ),
    );
  }
}

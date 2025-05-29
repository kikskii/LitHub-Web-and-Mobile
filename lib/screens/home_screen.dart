import 'package:flutter/material.dart';
import 'package:lithub_mobile/widgets/header_bar.dart';
import 'package:lithub_mobile/widgets/category_list.dart';
import 'package:lithub_mobile/widgets/promo_carousel.dart';
import 'package:lithub_mobile/widgets/feature_icons_row.dart';
import 'package:lithub_mobile/widgets/recommended_slider.dart';
import 'package:lithub_mobile/widgets/search_bar.dart';
import 'package:lithub_mobile/services/api_service.dart';
import 'dart:async';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  _HomeScreenState createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final TextEditingController _searchController = TextEditingController();
  List<dynamic> searchResults = [];
  Timer? _debounce;

  void _onSearch(String query) {
    if (_debounce?.isActive ?? false) _debounce!.cancel();
    _debounce = Timer(const Duration(milliseconds: 500), () async {
      if (query.isEmpty) {
        setState(() => searchResults = []);
        return;
      }
      
      try {
        final results = await ApiService.searchProducts(query);
        setState(() => searchResults = results);
      } catch (e) {
        print('Error searching: $e');
      }
    });
  }

  void _clearSearch() {
    _searchController.clear();
    setState(() => searchResults = []);
  }

  @override
  void dispose() {
    _searchController.dispose();
    _debounce?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.only(bottom: 80),
          child: Column(
            children: [
              const HeaderBar(),
              const SizedBox(height: 10),
              CustomSearchBar(
                controller: _searchController,
                onSearch: _onSearch,
                onClear: _clearSearch,
              ),
              const SizedBox(height: 10),
              CategoryList(), 
              const SizedBox(height: 10),
              const PromoCarousel(),
              const SizedBox(height: 20),
              const FeatureIconsRow(),
              const SizedBox(height: 20),
              const RecommendedSlider(),
              const SizedBox(height: 20),
              if (searchResults.isNotEmpty)
                Expanded(
                  child: ListView.builder(
                    itemCount: searchResults.length,
                    itemBuilder: (context, index) {
                      final product = searchResults[index];
                      return ListTile(
                        leading: Image.network(
                          '${ApiService.baseUrl}/static/images/${product['image']}',
                          width: 50,
                          height: 50,
                          fit: BoxFit.cover,
                        ),
                        title: Text(product['name']),
                        subtitle: Text('₱${product['price']}'),
                        onTap: () => Navigator.pushNamed(
                          context,
                          '/product',
                          arguments: {'productId': product['product_id']},
                        ),
                      );
                    },
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }
}

import 'package:flutter/material.dart';
import 'package:lithub_mobile/screens/home_screen.dart';
import 'package:lithub_mobile/screens/cart_screen.dart';
import 'package:lithub_mobile/screens/liked_screen.dart';
import 'package:lithub_mobile/screens/account/account_main_screen.dart';
import 'package:lithub_mobile/services/api_service.dart';

class MainNavigation extends StatefulWidget {
  const MainNavigation({super.key});

  @override
  State<MainNavigation> createState() => _MainNavigationState();
}

class _MainNavigationState extends State<MainNavigation> {
  int _currentIndex = 0;

  final List<Widget> _screens = [
    const HomeScreen(),
    CartScreen(),
    LikedScreen(),
    const AccountMainScreen(),
  ];

  Future<int> getCartCount() async {
    final cart = await ApiService.getCart();
    return cart.length;
  }

  Future<int> getLikedCount() async {
    final liked = await ApiService.getFavorites();
    return liked.length;
  }

  Widget buildIconWithBadge(IconData icon, Future<int> countFuture) {
    return FutureBuilder<int>(
      future: countFuture,
      builder: (context, snapshot) {
        int count = snapshot.data ?? 0;
        return Stack(
          clipBehavior: Clip.none,
          children: [
            Icon(icon),
            if (count > 0)
              Positioned(
                right: -6,
                top: -6,
                child: Container(
                  padding: const EdgeInsets.all(2),
                  decoration: BoxDecoration(
                    color: Colors.red,
                    borderRadius: BorderRadius.circular(10),
                  ),
                  constraints: const BoxConstraints(minWidth: 16, minHeight: 16),
                  child: Text(
                    '$count',
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 10,
                    ),
                    textAlign: TextAlign.center,
                  ),
                ),
              ),
          ],
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: SafeArea(child: _screens[_currentIndex]),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (index) => setState(() => _currentIndex = index),
        type: BottomNavigationBarType.fixed,
        selectedItemColor: Colors.deepPurple,
        unselectedItemColor: Colors.grey,
        showUnselectedLabels: true,
        backgroundColor: Colors.white,
        elevation: 10,
        items: [
          const BottomNavigationBarItem(icon: Icon(Icons.home), label: 'Home'),
          BottomNavigationBarItem(
            icon: buildIconWithBadge(Icons.shopping_cart, getCartCount()),
            label: 'Cart',
          ),
          BottomNavigationBarItem(
            icon: buildIconWithBadge(Icons.favorite, getLikedCount()),
            label: 'Liked',
          ),
          const BottomNavigationBarItem(icon: Icon(Icons.account_circle), label: 'Account'),
        ],
      ),
    );
  }
}

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'providers/cart_provider.dart';
import 'providers/auth_provider.dart';

import 'screens/splash_screen.dart';
import 'screens/start_page.dart';
import 'screens/login_screen.dart';
import 'screens/main_navigation.dart';
import 'screens/account/account_main_screen.dart';
import 'screens/account/account_settings_screen.dart';
import 'screens/account/account_edit_profile_screen.dart';
import 'screens/category_screen.dart';
import 'screens/product_details_screen.dart';
import 'screens/account/account_purchase.dart';
import 'screens/register_screen.dart';



void main() {
  runApp(const LitHubApp());
}

class LitHubApp extends StatelessWidget {
  const LitHubApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => CartProvider()),
        ChangeNotifierProvider(create: (_) => AuthProvider()),
      ],
      child: MaterialApp(
        debugShowCheckedModeBanner: false,
        title: 'LitHub',
        theme: ThemeData(
          colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
          useMaterial3: true,
          fontFamily: 'Roboto',
          scaffoldBackgroundColor: Colors.white,
        ),
        initialRoute: '/',
        routes: {
          '/': (context) => const SplashScreen(),
          '/start': (context) => const StartPage(),
          '/login': (context) => const LoginScreen(),
          '/register': (context) => const RegisterScreen(),
          '/main': (context) => const MainNavigation(),
          '/account': (context) => const AccountMainScreen(),
          '/account/settings': (context) => const AccountSettingsScreen(),
          '/account/edit': (context) => const AccountEditProfileScreen(),
          '/account/purchases': (context) => const AccountPurchaseScreen(),
          '/category': (context) {
            final args = ModalRoute.of(context)!.settings.arguments as Map<String, dynamic>;
            return CategoryScreen(
              categoryLabel: args['label'] ?? '',
              categoryValue: args['value'] ?? '',
            );
          },
          '/product': (context) {
          final args = ModalRoute.of(context)!.settings.arguments as Map<String, dynamic>;
          return ProductDetailsScreen(productId: args['productId']);
},



        },
      ),
    );
  }
}

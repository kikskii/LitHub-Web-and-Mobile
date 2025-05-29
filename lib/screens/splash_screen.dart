import 'package:flutter/material.dart';
import 'dart:async';
import 'package:provider/provider.dart';
import 'package:lithub_mobile/services/api_service.dart';
import 'package:lithub_mobile/services/storage_service.dart';
import 'package:lithub_mobile/providers/auth_provider.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  @override
  void initState() {
    super.initState();
    _checkAuth();
  }

  Future<void> _checkAuth() async {
    final token = await StorageService.getToken();
    if (token != null) {
      try {
        final user = await ApiService.getUserProfile();
        if (mounted) {
          Provider.of<AuthProvider>(context, listen: false).login(user);
          Navigator.pushReplacementNamed(context, '/main');
        }
      } catch (e) {
        // token might be invalid or expired
        if (mounted) {
          Navigator.pushReplacementNamed(context, '/start');
        }
      }
    } else {
      Navigator.pushReplacementNamed(context, '/start');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: Center(
        child: Image.asset('assets/logo.png', height: 100),
      ),
    );
  }
}

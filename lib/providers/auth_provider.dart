import 'package:flutter/material.dart';
import 'package:lithub_mobile/services/api_service.dart';
import 'package:lithub_mobile/services/storage_service.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class AuthProvider with ChangeNotifier {
  Map<String, dynamic>? _user;

  Map<String, dynamic>? get user => _user;

  bool get isLoggedIn => _user != null;

  void login(Map<String, dynamic> userData) {
    _user = userData;
    notifyListeners();
  }

  void logout() {
    _user = null;
    notifyListeners();
  }

  void setUser(Map<String, dynamic> updatedUser) {
    _user = {...?_user, ...updatedUser};
    notifyListeners();
  }

  Future<void> refreshUserProfile() async {
    try {
      final token = await StorageService.getToken();
      if (token == null) return;

      final response = await http.get(
        Uri.parse('${ApiService.baseUrl}/api/account'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      );

      print('API /api/account response: ${response.body}');

      if (response.statusCode == 200) {
        final userData = json.decode(response.body);
        _user = userData;
        notifyListeners();
      }
    } catch (e) {
      print('Error refreshing user profile: $e');
    }
  }
}

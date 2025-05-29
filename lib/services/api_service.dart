import 'package:http/http.dart' as http;
import 'dart:convert';
import 'storage_service.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:io';


class ApiService {

  static String get baseUrl {
 
    return 'http://192.168.1.16:5000';  
  }

  // 🔑 LOGIN
  static Future<Map<String, dynamic>> login(String email, String password) async {
    try {
      print("[API Service] Attempting login for email: $email");
      print("[API Service] Using base URL: $baseUrl");
      
      final res = await http.post(
        Uri.parse('$baseUrl/api/login'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'email': email, 'password': password}),
      ).timeout(const Duration(seconds: 15));

      print("[API Service] Login response status: ${res.statusCode}");
      print("[API Service] Login response body: ${res.body}");

      if (res.statusCode == 200) {
        final responseData = jsonDecode(res.body);
        
        // Store token immediately
        if (responseData['access_token'] != null) {
          await StorageService.saveToken(responseData['access_token']);
          print("[API Service] Token saved successfully");
        } else {
          print("[API Service] Warning: No token in response");
        }
        
        return responseData;
      } else {
        print("[API Service] Login failed with status: ${res.statusCode}");
        throw Exception('Failed to login: ${res.statusCode} - ${res.body}');
      }
    } catch (e) {
      print("[API Service] Login exception: $e");
      throw Exception('Connection error. Please check if the server is running and accessible.');
    }
  }

  // 📦 GET PRODUCTS
  static Future<List<dynamic>> getProducts() async {
  try {
    final response = await http.get(Uri.parse('$baseUrl/api/products'));
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      print('Failed to load products. Status: ${response.statusCode}');
      return [];
    }
  } catch (e) {
    print('Error: $e');
    return [];
  }
}


  // 🛒 GET CART
static Future<List<dynamic>> getCart() async {
  final token = await StorageService.getToken();
  if (token == null) {
    print('[getCart] No token found. User not authenticated.');
    return [];
  }

  try {
    print('[getCart] Token: $token');
    final res = await http.get(
      Uri.parse('$baseUrl/api/cart'),
      headers: {'Authorization': 'Bearer $token'},
    );

    if (res.statusCode == 200) {
      print('[getCart] Success: ${res.body}');
      return jsonDecode(res.body);
    } else {
      print('[getCart] Failed: ${res.statusCode} - ${res.body}');
      return [];
    }
  } catch (e) {
    print('[getCart] Exception: $e');
    return [];
  }
}



  // ❤️ GET FAVORITES
  static Future<List<dynamic>> getFavorites() async {
  final token = await StorageService.getToken();
  if (token == null) {
    print('[getFavorites] No token found. User not authenticated.');
    return [];
  }

  try {
    print('[getFavorites] Token: $token');
    final res = await http.get(
      Uri.parse('$baseUrl/api/favorites'),
      headers: {'Authorization': 'Bearer $token'},
    );

    if (res.statusCode == 200) {
      print('[getFavorites] Success: ${res.body}');
      return jsonDecode(res.body);
    } else {
      print('[getFavorites] Failed: ${res.statusCode} - ${res.body}');
      return [];
    }
  } catch (e) {
    print('[getFavorites] Exception: $e');
    return [];
  }
}


  static Future<List<dynamic>> getProductsByCategory(String category) async {
  try {
    final response = await http.get(
      Uri.parse('$baseUrl/api/products/category/${Uri.encodeComponent(category)}'),
    );
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      print('Failed to load category products: ${response.statusCode}');
      return [];
    }
  } catch (e) {
    print('Error: $e');
    return [];
  }
}

static Future<Map<String, dynamic>> getProductDetails(int productId) async {
  final token = await StorageService.getToken();
  if (token == null) {
    print('[getProductDetails] Token is null. User not authenticated.');
    throw Exception('Not authenticated');
  }

  final res = await http.get(
    Uri.parse('$baseUrl/api/product/$productId'),
    headers: {'Authorization': 'Bearer $token'},
  );

  print('[getProductDetails] Status: ${res.statusCode}');
  print('[getProductDetails] Body: ${res.body}');

  if (res.statusCode == 200) {
    return jsonDecode(res.body);
  } else {
    throw Exception('Failed to load product: ${res.statusCode} - ${res.body}');
  }
}



// 🛒 Add to Cart
static Future<bool> addToCart(int productId, int quantity) async {
  final token = await StorageService.getToken();
  if (token == null) return false;

  final res = await http.post(
    Uri.parse('$baseUrl/api/cart'),
    headers: {
      'Authorization': 'Bearer $token',
      'Content-Type': 'application/json',
    },
    body: jsonEncode({
      'product_id': productId,
      'quantity': quantity,
    }),
  );

  return res.statusCode == 200;
}

static Future<bool> updateCartQuantity(int productId, int quantity) async {
  final token = await StorageService.getToken();
  if (token == null) return false;

  final res = await http.put(
    Uri.parse('$baseUrl/api/cart/$productId'),
    headers: {
      'Authorization': 'Bearer $token',
      'Content-Type': 'application/json',
    },
    body: jsonEncode({'quantity': quantity}),
  );

  return res.statusCode == 200;
}

static Future<bool> removeFromCart(int productId) async {
  final token = await StorageService.getToken();
  if (token == null) return false;

  final res = await http.delete(
    Uri.parse('$baseUrl/api/cart/$productId'),
    headers: {'Authorization': 'Bearer $token'},
  );

  return res.statusCode == 200;
}


  // ✅ CHECKOUT
  static Future<Map<String, dynamic>> checkout(List<dynamic> cartItems, double total, String paymentMethod) async {
  final token = await getToken();

  final res = await http.post(
    Uri.parse('$baseUrl/api/checkout'),
    headers: {
      'Authorization': 'Bearer $token',
      'Content-Type': 'application/json',
    },
    body: jsonEncode({
      'cart': cartItems,
      'total': total,
      'payment_method': paymentMethod,
    }),
  );

  if (res.statusCode == 200) {
    return {'success': true, 'data': jsonDecode(res.body)};
  } else {
    return {'success': false, 'error': jsonDecode(res.body)['error'] ?? 'Unknown error'};
  }
}


  // 📝 REGISTER
  static Future<Map<String, dynamic>> register(String name, String email, String password) async {
    final res = await http.post(
      Uri.parse('$baseUrl/api/register'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'name': name, 'email': email, 'password': password}),
    );
    return jsonDecode(res.body);
  }

  static Future<List<dynamic>> getPromos() async {
  try {
    final res = await http.get(Uri.parse('$baseUrl/api/promos'));
    if (res.statusCode == 200) {
      return jsonDecode(res.body);
    } else {
      print('Failed to load promos');
      return [];
    }
  } catch (e) {
    print('Error loading promos: $e');
    return [];
  }
}


  // 🔒 FORGOT PASSWORD
  static Future<Map<String, dynamic>> forgotPassword(String email) async {
    final res = await http.post(
      Uri.parse('$baseUrl/api/forgot-password'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'email': email}),
    );
    return jsonDecode(res.body);
  }


  static Future<String?> getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('access_token');
  }

  static Future<Map<String, dynamic>> getUserProfile() async {
    final token = await getToken();
    final res = await http.get(
      Uri.parse('$baseUrl/api/account'),
      headers: {'Authorization': 'Bearer $token'},
    );
    
    if (res.statusCode == 200) {
      final data = jsonDecode(res.body);
      // Ensure profile_picture is included in the response
      print("Profile data: ${data}"); // Debug log
      return data;
    } else {
      throw Exception('Failed to load profile');
    }
  }

  static Future<bool> updateUserProfile(Map<String, dynamic> data) async {
    final token = await getToken();
    final res = await http.put(
      Uri.parse('$baseUrl/api/account'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
      body: jsonEncode(data),
    );
    return res.statusCode == 200;
  }

  static Future<void> logout() async {
  final prefs = await SharedPreferences.getInstance();
  await prefs.remove('access_token');
}

  static Future<Map<String, dynamic>> getOrderDetails(int orderId) async {
    final token = await StorageService.getToken();
    
    try {
      print("[API Service] Getting order details for order ID: $orderId");
      final res = await http.get(
        Uri.parse('$baseUrl/api/orders/$orderId'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json'
        },
      ).timeout(const Duration(seconds: 10));
      
      print("[API Service] Order details response status: ${res.statusCode}");
      print("[API Service] Order details response body: ${res.body}");
      
      if (res.statusCode == 200) {
        return jsonDecode(res.body);
      } else {
        throw Exception('Failed to get order details: ${res.statusCode}');
      }
    } catch (e) {
      print("[API Service] Error getting order details: $e");
      rethrow;
    }
  }

  static Future<List<dynamic>> getUserOrders({String? status}) async {
  final token = await StorageService.getToken();
  
  try {
    String url = '$baseUrl/api/orders';
    if (status != null && status != 'all') {
      url += '?status=$status';
    }
    
    final res = await http.get(
      Uri.parse(url),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json'
      },
    ).timeout(const Duration(seconds: 10));
    
    if (res.statusCode == 200) {
      return jsonDecode(res.body);
    } else {
      throw Exception('Failed to get orders: ${res.statusCode}');
    }
  } catch (e) {
    print("[API Service] Error getting orders: $e");
    rethrow;
  }
}

static Future<List<dynamic>> searchUserOrders(String query) async {
  final token = await StorageService.getToken();
  
  try {
    final res = await http.get(
      Uri.parse('$baseUrl/api/orders/search?q=$query'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json'
      },
    ).timeout(const Duration(seconds: 10));
    
    if (res.statusCode == 200) {
      return jsonDecode(res.body);
    } else {
      throw Exception('Failed to search orders: ${res.statusCode}');
    }
  } catch (e) {
    print("[API Service] Error searching orders: $e");
    rethrow;
  }
}

static Future<bool> updateOrderStatus(int orderId, String status) async {
  final token = await StorageService.getToken();
  
  try {
    final res = await http.post(
      Uri.parse('$baseUrl/api/orders/$orderId/status'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json'
      },
      body: jsonEncode({'status': status}),
    );
    
    if (res.statusCode == 200) {
      return true;
    } else {
      throw Exception('Failed to update order status: ${res.statusCode}');
    }
  } catch (e) {
    print("[API Service] Error updating order status: $e");
    rethrow;
  }
}

static Future<bool> submitRating(Map<String, dynamic> ratingData) async {
  final token = await StorageService.getToken();
  
  try {
    final res = await http.post(
      Uri.parse('$baseUrl/api/submit_rating'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json'
      },
      body: jsonEncode(ratingData),
    );
    
    if (res.statusCode == 200) {
      return true;
    } else {
      throw Exception('Failed to submit rating: ${res.statusCode}');
    }
  } catch (e) {
    print("[API Service] Error submitting rating: $e");
    rethrow;
  }
}

static Future<Map<String, dynamic>> updateProfile(Map<String, dynamic> userData) async {
  final token = await StorageService.getToken();
  
  try {
    final res = await http.post(
      Uri.parse('$baseUrl/api/profile/update'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json'
      },
      body: jsonEncode(userData),
    );
    
    if (res.statusCode == 200) {
      return jsonDecode(res.body);
    } else {
      throw Exception('Failed to update profile: ${res.statusCode}');
    }
  } catch (e) {
    print("[API Service] Error updating profile: $e");
    rethrow;
  }
}

static Future<Map<String, dynamic>> updateProfilePicture(File imageFile) async {
  final token = await StorageService.getToken();
  
  try {
    final request = http.MultipartRequest(
      'POST',
      Uri.parse('$baseUrl/api/profile/update_picture'),
    );
    
    request.headers['Authorization'] = 'Bearer $token';
    request.files.add(await http.MultipartFile.fromPath(
      'profile_picture',
      imageFile.path,
    ));
    
    final streamedResponse = await request.send();
    final response = await http.Response.fromStream(streamedResponse);
    
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to update profile picture: ${response.statusCode}');
    }
  } catch (e) {
    print("[API Service] Error updating profile picture: $e");
    rethrow;
  }
}
  static Future<List<dynamic>> getNotifications() async {
    final token = await StorageService.getToken();
    if (token == null) return [];

    try {
      final res = await http.get(
        Uri.parse('$baseUrl/api/notifications'),
        headers: {'Authorization': 'Bearer $token'},
      );

      if (res.statusCode == 200) {
        return jsonDecode(res.body);
      } else {
        print('[getNotifications] Failed: ${res.statusCode}');
        return [];
      }
    } catch (e) {
      print('[getNotifications] Error: $e');
      return [];
    }
  }

  static Future<bool> markNotificationAsRead(int notifId) async {
    final token = await StorageService.getToken();
    if (token == null) return false;

    try {
      final res = await http.post(
        Uri.parse('$baseUrl/api/notification/read'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
        body: jsonEncode({'notification_id': notifId}),
      );
      return res.statusCode == 200 && jsonDecode(res.body)['success'] == true;
    } catch (e) {
      print('[markNotificationAsRead] Error: $e');
      return false;
    }
  }

  static Future<bool> deleteNotification(int notifId) async {
    final token = await StorageService.getToken();
    if (token == null) return false;

    try {
      final res = await http.delete(
        Uri.parse('$baseUrl/api/notification/$notifId'),
        headers: {'Authorization': 'Bearer $token'},
      );
      return res.statusCode == 200 && jsonDecode(res.body)['success'] == true;
    } catch (e) {
      print('[deleteNotification] Error: $e');
      return false;
    }
  }

  static Future<int> getUnreadCount() async {
    final token = await StorageService.getToken();
    if (token == null) return 0;

    try {
      final res = await http.get(
        Uri.parse('$baseUrl/api/notifications/unread_count'),
        headers: {'Authorization': 'Bearer $token'},
      );
      if (res.statusCode == 200) {
        return jsonDecode(res.body)['count'] ?? 0;
      }
    } catch (e) {
      print('[getUnreadCount] Error: $e');
    }
    return 0;
  }

  static Future<bool> markAllNotificationsAsRead() async {
    final token = await StorageService.getToken();
    if (token == null) return false;

    try {
      final res = await http.post(
        Uri.parse('$baseUrl/api/notifications/mark_all_read'),
        headers: {'Authorization': 'Bearer $token'},
      );
      return res.statusCode == 200 && jsonDecode(res.body)['success'] == true;
    } catch (e) {
      print('[markAllNotificationsAsRead] Error: $e');
      return false;
    }
  }

  static Future<int> getUnreadNotificationCount() async {
    try {
      final token = await StorageService.getToken();
      final response = await http.get(
        Uri.parse('$baseUrl/api/notifications/unread/count'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['count'] ?? 0;
      }
      return 0;
    } catch (e) {
      print('Error getting unread notification count: $e');
      return 0;
    }
  }

  static Future<List<dynamic>> getConversations() async {
    try {
      final token = await StorageService.getToken();
      final response = await http.get(
        Uri.parse('$baseUrl/api/messages'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['messages'] ?? [];
      }
      return [];
    } catch (e) {
      print('Error getting conversations: $e');
      return [];
    }
  }

  static Future<List<dynamic>> getChatMessages(int otherUserId) async {
    try {
      final token = await StorageService.getToken();
      final response = await http.get(
        Uri.parse('$baseUrl/api/messages/$otherUserId'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['messages'] ?? [];
      }
      return [];
    } catch (e) {
      print('Error getting chat messages: $e');
      return [];
    }
  }

  static Future<bool> sendMessage(int receiverId, String message) async {
    try {
      final token = await StorageService.getToken();
      final response = await http.post(
        Uri.parse('$baseUrl/api/messages/send'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'receiver_id': receiverId,
          'message': message,
        }),
      );

      return response.statusCode == 200;
    } catch (e) {
      print('Error sending message: $e');
      return false;
    }
  }

  static Future<int> getUnreadMessageCount() async {
    try {
      final token = await StorageService.getToken();
      final response = await http.get(
        Uri.parse('$baseUrl/api/notifications/unread/count'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['count'] ?? 0;
      }
      return 0;
    } catch (e) {
      print('Error getting unread message count: $e');
      return 0;
    }
  }

  static Future<List<dynamic>> getMessages() async {
    try {
      final token = await StorageService.getToken();
      final response = await http.get(
        Uri.parse('$baseUrl/api/conversations'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['conversations'] ?? [];
      }
      return [];
    } catch (e) {
      print('Error getting messages: $e');
      return [];
    }
  }

  static Future<bool> toggleFavorite(int productId) async {
    try {
      final token = await StorageService.getToken();
      final response = await http.post(
        Uri.parse('$baseUrl/api/favorites/toggle'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
        body: jsonEncode({'product_id': productId}),
      );
      return response.statusCode == 200;
    } catch (e) {
      print('Error toggling favorite: $e');
      return false;
    }
  }

  // Fetch unread counts
static Future<Map<String, dynamic>> getUnreadCounts() async {
  final token = await StorageService.getToken();
  final res = await http.get(
    Uri.parse('$baseUrl/api/unread_counts'),
    headers: {'Authorization': 'Bearer $token'},
  );
  if (res.statusCode == 200) {
    return jsonDecode(res.body);
  } else {
    throw Exception('Failed to fetch unread counts');
  }
}

// Contact seller via order ID
static Future<Map<String, dynamic>> contactSeller(int orderId) async {
  final token = await StorageService.getToken();
  final res = await http.post(
    Uri.parse('$baseUrl/api/contact_seller/$orderId'),
    headers: {'Authorization': 'Bearer $token'},
  );
  final data = jsonDecode(res.body);
  if (res.statusCode == 200 && data['success']) {
    return data['seller'];
  } else {
    throw Exception(data['message'] ?? 'Failed to contact seller');
  }
}

static Future<List<dynamic>> searchProducts(String query) async {
  try {
    final token = await StorageService.getToken();
    final response = await http.get(
      Uri.parse('$baseUrl/api/products/search?q=$query'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return data['products'] ?? [];
    }
    return [];
  } catch (e) {
    print('Error searching products: $e');
    return [];
  }
}

static Future<Map<String, dynamic>?> getOrderById(int orderId) async {
  final token = await StorageService.getToken();
  final response = await http.get(
    Uri.parse('$baseUrl/api/orders/$orderId'),
    headers: {
      'Authorization': 'Bearer $token',
      'Content-Type': 'application/json',
    },
  );
  if (response.statusCode == 200) {
    return json.decode(response.body);
  } else {
    print('Failed to fetch order: ${response.body}');
    return null;
  }
}

}

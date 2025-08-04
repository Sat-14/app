import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import '../config/api_config.dart';
import '../models/bill.dart';
import '../models/user.dart';
import '../models/payment.dart';
import '../models/notification.dart';
import 'storage_service.dart';

class ApiService {
  // Authentication methods
  static Future<Map<String, dynamic>> login(String email, String password) async {
    try {
      final response = await http.post(
        Uri.parse('${ApiConfig.baseUrl}${ApiConfig.loginEndpoint}'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'email': email,
          'password': password,
        }),
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception(json.decode(response.body)['message'] ?? 'Login failed');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  // Profile update
  static Future<User> updateProfile(String name, String phoneNumber) async {
    try {
      final token = await StorageService.getToken();
      final response = await http.put(
        Uri.parse('${ApiConfig.baseUrl}${ApiConfig.updateProfileEndpoint}'),
        headers: ApiConfig.getHeaders(token),
        body: json.encode({
          'name': name,
          'phone_number': phoneNumber,
        }),
      );

      if (response.statusCode == 200) {
        return User.fromJson(json.decode(response.body));
      } else {
        throw Exception('Failed to update profile');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  // Reminder settings
  static Future<Map<String, dynamic>> getReminderSettings() async {
    try {
      final token = await StorageService.getToken();
      final response = await http.get(
        Uri.parse('${ApiConfig.baseUrl}${ApiConfig.reminderSettingsEndpoint}'),
        headers: ApiConfig.getHeaders(token),
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to get reminder settings');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  static Future<void> updateReminderSettings(Map<String, dynamic> settings) async {
    try {
      final token = await StorageService.getToken();
      final response = await http.put(
        Uri.parse('${ApiConfig.baseUrl}${ApiConfig.reminderSettingsEndpoint}'),
        headers: ApiConfig.getHeaders(token),
        body: json.encode(settings),
      );

      if (response.statusCode != 200) {
        throw Exception('Failed to update reminder settings');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  static Future<void> testReminder(String type) async {
    try {
      final token = await StorageService.getToken();
      final response = await http.post(
        Uri.parse('${ApiConfig.baseUrl}${ApiConfig.testReminderEndpoint}'),
        headers: ApiConfig.getHeaders(token),
        body: json.encode({'type': type}),
      );

      if (response.statusCode != 200) {
        throw Exception('Failed to send test reminder');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }


  static Future<Map<String, dynamic>> register(String email, String password, String name, String phoneNumber) async {
    try {
      final response = await http.post(
        Uri.parse('${ApiConfig.baseUrl}${ApiConfig.registerEndpoint}'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'email': email,
          'password': password,
          'name': name,
          'phone_number': phoneNumber,
        }),
      );

      if (response.statusCode == 201) {
        return json.decode(response.body);
      } else {
        throw Exception(json.decode(response.body)['message'] ?? 'Registration failed');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  static Future<void> logout() async {
    try {
      final token = await StorageService.getToken();
      await http.post(
        Uri.parse('${ApiConfig.baseUrl}${ApiConfig.logoutEndpoint}'),
        headers: ApiConfig.getHeaders(token),
      );
    } catch (e) {
      // Logout anyway locally even if API call fails
    }
  }

  // Bills methods
  static Future<List<Bill>> getBills() async {
    try {
      final token = await StorageService.getToken();
      final response = await http.get(
        Uri.parse('${ApiConfig.baseUrl}${ApiConfig.billsEndpoint}'),
        headers: ApiConfig.getHeaders(token),
      );

      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(response.body);
        return data.map((json) => Bill.fromJson(json)).toList();
      } else {
        throw Exception('Failed to load bills');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  static Future<Bill> createBill(Bill bill) async {
    try {
      final token = await StorageService.getToken();
      final response = await http.post(
        Uri.parse('${ApiConfig.baseUrl}${ApiConfig.billsEndpoint}'),
        headers: ApiConfig.getHeaders(token),
        body: json.encode(bill.toJson()),
      );

      if (response.statusCode == 201) {
        return Bill.fromJson(json.decode(response.body));
      } else {
        throw Exception('Failed to create bill');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  static Future<Bill> updateBill(String id, Bill bill) async {
    try {
      final token = await StorageService.getToken();
      final response = await http.put(
        Uri.parse('${ApiConfig.baseUrl}${ApiConfig.billsEndpoint}/$id'),
        headers: ApiConfig.getHeaders(token),
        body: json.encode(bill.toJson()),
      );

      if (response.statusCode == 200) {
        return Bill.fromJson(json.decode(response.body));
      } else {
        throw Exception('Failed to update bill');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  static Future<void> deleteBill(String id) async {
    try {
      final token = await StorageService.getToken();
      final response = await http.delete(
        Uri.parse('${ApiConfig.baseUrl}${ApiConfig.billsEndpoint}/$id'),
        headers: ApiConfig.getHeaders(token),
      );

      if (response.statusCode != 204 && response.statusCode != 200) {
        throw Exception('Failed to delete bill');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  static Future<void> markBillAsPaid(String id) async {
    try {
      final token = await StorageService.getToken();
      final response = await http.post(
        Uri.parse('${ApiConfig.baseUrl}${ApiConfig.billsEndpoint}/$id/pay'),
        headers: ApiConfig.getHeaders(token),
      );

      if (response.statusCode != 200) {
        throw Exception('Failed to mark bill as paid');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  // Payments methods
  static Future<List<Payment>> getPayments() async {
    try {
      final token = await StorageService.getToken();
      final response = await http.get(
        Uri.parse('${ApiConfig.baseUrl}${ApiConfig.paymentsEndpoint}'),
        headers: ApiConfig.getHeaders(token),
      );

      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(response.body);
        return data.map((json) => Payment.fromJson(json)).toList();
      } else {
        throw Exception('Failed to load payments');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  static Future<Payment> recordPayment(Payment payment) async {
    try {
      final token = await StorageService.getToken();
      final response = await http.post(
        Uri.parse('${ApiConfig.baseUrl}${ApiConfig.paymentsEndpoint}'),
        headers: ApiConfig.getHeaders(token),
        body: json.encode(payment.toJson()),
      );

      if (response.statusCode == 201) {
        return Payment.fromJson(json.decode(response.body));
      } else {
        throw Exception('Failed to record payment');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  // Notifications methods
  static Future<List<NotificationModel>> getNotifications() async {
    try {
      final token = await StorageService.getToken();
      final response = await http.get(
        Uri.parse('${ApiConfig.baseUrl}${ApiConfig.notificationsEndpoint}'),
        headers: ApiConfig.getHeaders(token),
      );

      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(response.body);
        return data.map((json) => NotificationModel.fromJson(json)).toList();
      } else {
        throw Exception('Failed to load notifications');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  static Future<void> markNotificationRead(String id) async {
    try {
      final token = await StorageService.getToken();
      final response = await http.put(
        Uri.parse('${ApiConfig.baseUrl}${ApiConfig.notificationsEndpoint}/$id/read'),
        headers: ApiConfig.getHeaders(token),
      );

      if (response.statusCode != 200) {
        throw Exception('Failed to mark notification as read');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  // Receipt scanning
  static Future<Bill> scanReceipt(File imageFile) async {
    try {
      final token = await StorageService.getToken();
      
      var request = http.MultipartRequest(
        'POST',
        Uri.parse('${ApiConfig.baseUrl}${ApiConfig.scanReceiptEndpoint}'),
      );
      
      request.headers.addAll(ApiConfig.getMultipartHeaders(token));
      request.files.add(await http.MultipartFile.fromPath(
        'receipt',
        imageFile.path,
      ));

      final streamedResponse = await request.send();
      final response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 200) {
        return Bill.fromJson(json.decode(response.body));
      } else {
        throw Exception('Failed to scan receipt');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }
}
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';
import '../models/user.dart';

class StorageService {
  static late SharedPreferences _prefs;
  
  static const String _tokenKey = 'auth_token';
  static const String _userKey = 'user_data';
  static const String _themeKey = 'is_dark_mode';

  static Future<void> init() async {
    _prefs = await SharedPreferences.getInstance();
  }

  // Token management
  static Future<void> saveToken(String token) async {
    await _prefs.setString(_tokenKey, token);
  }

  static Future<String?> getToken() async {
    return _prefs.getString(_tokenKey);
  }

  static Future<void> removeToken() async {
    await _prefs.remove(_tokenKey);
  }

  // User management
  static Future<void> saveUser(User user) async {
    await _prefs.setString(_userKey, json.encode(user.toJson()));
  }

  static Future<User?> getUser() async {
    final userData = _prefs.getString(_userKey);
    if (userData != null) {
      return User.fromJson(json.decode(userData));
    }
    return null;
  }

  static Future<void> removeUser() async {
    await _prefs.remove(_userKey);
  }

  // Theme management
  static Future<void> saveTheme(bool isDarkMode) async {
    await _prefs.setBool(_themeKey, isDarkMode);
  }

  static bool getTheme() {
    return _prefs.getBool(_themeKey) ?? false;
  }

  // Clear all data
  static Future<void> clearAll() async {
    await _prefs.clear();
  }

  // Check if user is logged in
  static bool isLoggedIn() {
    return _prefs.getString(_tokenKey) != null;
  }
}
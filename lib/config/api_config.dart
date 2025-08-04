class ApiConfig {
  // Change this to your Flask server URL
  static const String baseUrl = 'http://127.0.0.1:5000';
  
  // Authentication endpoints
  static const String loginEndpoint = '/auth/login';
  static const String registerEndpoint = '/auth/register';
  static const String logoutEndpoint = '/auth/logout';
  static const String updateProfileEndpoint = '/auth/profile';
  
  // Bills endpoints
  static const String billsEndpoint = '/bills';
  
  // Payments endpoints
  static const String paymentsEndpoint = '/payments';
  
  // Notifications endpoints
  static const String notificationsEndpoint = '/notifications';
  
  // Reminder endpoints
  static const String reminderSettingsEndpoint = '/reminders/settings';
  static const String testReminderEndpoint = '/reminders/test';
  
  // Receipt scanning endpoint
  static const String scanReceiptEndpoint = '/bills/scan-receipt';

  static Map<String, String> getHeaders(String? token) {
    return {
      'Content-Type': 'application/json',
      if (token != null) 'Authorization': 'Bearer $token',
    };
  }

  static Map<String, String> getMultipartHeaders(String? token) {
    return {
      if (token != null) 'Authorization': 'Bearer $token',
    };
  }
}
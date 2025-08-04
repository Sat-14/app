import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'providers/auth_provider.dart';
import 'providers/bill_provider.dart';
import 'providers/theme_provider.dart';
import 'package:final_wali_file/services/storage_service.dart';
import 'services/notification_service.dart';
import 'screens/auth/login_screen.dart';         // ✅ NEW
import 'screens/main_navigation.dart';


void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await StorageService.init();
  await NotificationService.initialize();
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthProvider()),
        ChangeNotifierProvider(create: (_) => BillProvider()),
        ChangeNotifierProvider(create: (_) => ThemeProvider()),
      ],
      child: Consumer<ThemeProvider>(
        builder: (context, themeProvider, child) {
          return MaterialApp(
            title: 'Bills Reminder',
            theme: themeProvider.currentTheme,
            home: const AuthWrapper(),
            debugShowCheckedModeBanner: false,
          );
        },
      ),
    );
  }
}

class AuthWrapper extends StatelessWidget {
  const AuthWrapper({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer<AuthProvider>(
      builder: (context, authProvider, child) {
        if (authProvider.isAuthenticated) {
          return const MainNavigation();
        }
        return const LoginScreen();
      },
    );
  }
}
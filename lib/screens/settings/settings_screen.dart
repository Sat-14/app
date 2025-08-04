import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';
import '../../providers/theme_provider.dart';
import 'profile_edit_screen.dart';
import 'reminder_settings_screen.dart';


class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final authProvider = context.watch<AuthProvider>();
    final themeProvider = context.watch<ThemeProvider>();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Settings'),
      ),
      body: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Profile section
            Card(
              margin: const EdgeInsets.all(16),
              child: InkWell(
                onTap: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (context) => const ProfileEditScreen()),
                  );
                },
                borderRadius: BorderRadius.circular(12),
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Row(
                    children: [
                      CircleAvatar(
                        radius: 30,
                        child: Text(
                          authProvider.user?.name[0].toUpperCase() ?? 'U',
                          style: const TextStyle(fontSize: 24),
                        ),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              authProvider.user?.name ?? 'User',
                              style: const TextStyle(
                                fontSize: 18,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              authProvider.user?.email ?? '',
                              style: TextStyle(
                                color: Colors.grey[600],
                              ),
                            ),
                            if (authProvider.user?.phoneNumber != null &&
                                authProvider.user!.phoneNumber!.isNotEmpty) ...[
                              const SizedBox(height: 2),
                              Text(
                                authProvider.user!.phoneNumber!,
                                style: TextStyle(
                                  color: Colors.grey[600],
                                  fontSize: 12,
                                ),
                              ),
                            ],
                          ],
                        ),
                      ),
                      const Icon(Icons.arrow_forward_ios, size: 16),
                    ],
                  ),
                ),
              ),
            ),

            // Settings sections
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: Text(
                'PREFERENCES',
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                  color: Colors.grey[600],
                ),
              ),
            ),
            const SizedBox(height: 8),

            // Theme toggle
            ListTile(
              leading: const Icon(Icons.dark_mode),
              title: const Text('Dark Mode'),
              subtitle: const Text('Switch between light and dark theme'),
              trailing: Switch(
                value: themeProvider.isDarkMode,
                onChanged: (value) {
                  themeProvider.toggleTheme();
                },
              ),
            ),

            // Notifications
            ListTile(
              leading: const Icon(Icons.notifications),
              title: const Text('Reminder Settings'),
              subtitle: const Text('Manage all reminder preferences'),
              trailing: const Icon(Icons.arrow_forward_ios, size: 16),
              onTap: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (context) => const ReminderSettingsScreen()),
                );
              },
            ),

            const Divider(height: 32),

            // Data section
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: Text(
                'DATA',
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                  color: Colors.grey[600],
                ),
              ),
            ),
            const SizedBox(height: 8),

            // Export data
            ListTile(
              leading: const Icon(Icons.download),
              title: const Text('Export Data'),
              subtitle: const Text('Download your bills data as CSV'),
              trailing: const Icon(Icons.arrow_forward_ios, size: 16),
              onTap: () {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('Export feature coming soon!'),
                  ),
                );
              },
            ),

            // Clear cache
            ListTile(
              leading: const Icon(Icons.cleaning_services),
              title: const Text('Clear Cache'),
              subtitle: const Text('Free up storage space'),
              trailing: const Icon(Icons.arrow_forward_ios, size: 16),
              onTap: () async {
                final confirmed = await showDialog<bool>(
                  context: context,
                  builder: (context) => AlertDialog(
                    title: const Text('Clear Cache'),
                    content: const Text('This will remove all cached data. Are you sure?'),
                    actions: [
                      TextButton(
                        onPressed: () => Navigator.pop(context, false),
                        child: const Text('Cancel'),
                      ),
                      TextButton(
                        onPressed: () => Navigator.pop(context, true),
                        style: TextButton.styleFrom(
                          foregroundColor: Colors.red,
                        ),
                        child: const Text('Clear'),
                      ),
                    ],
                  ),
                );

                if (confirmed == true) {
                  // Clear cache logic
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('Cache cleared successfully'),
                      backgroundColor: Colors.green,
                    ),
                  );
                }
              },
            ),

            const Divider(height: 32),

            // Support section
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: Text(
                'SUPPORT',
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                  color: Colors.grey[600],
                ),
              ),
            ),
            const SizedBox(height: 8),

            // Help & FAQ
            ListTile(
              leading: const Icon(Icons.help),
              title: const Text('Help & FAQ'),
              trailing: const Icon(Icons.arrow_forward_ios, size: 16),
              onTap: () {
                // Navigate to help screen
              },
            ),

            // About
            ListTile(
              leading: const Icon(Icons.info),
              title: const Text('About'),
              trailing: const Icon(Icons.arrow_forward_ios, size: 16),
              onTap: () {
                showAboutDialog(
                  context: context,
                  applicationName: 'Bills Reminder',
                  applicationVersion: '1.0.0',
                  applicationIcon: const Icon(Icons.receipt_long, size: 48),
                  children: [
                    const Text('A simple app to manage and track your bills.'),
                  ],
                );
              },
            ),

            // Privacy Policy
            ListTile(
              leading: const Icon(Icons.privacy_tip),
              title: const Text('Privacy Policy'),
              trailing: const Icon(Icons.arrow_forward_ios, size: 16),
              onTap: () {
                // Open privacy policy
              },
            ),

            const Divider(height: 32),

            // Logout
            Padding(
              padding: const EdgeInsets.all(16),
              child: SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: () async {
                    final confirmed = await showDialog<bool>(
                      context: context,
                      builder: (context) => AlertDialog(
                        title: const Text('Logout'),
                        content: const Text('Are you sure you want to logout?'),
                        actions: [
                          TextButton(
                            onPressed: () => Navigator.pop(context, false),
                            child: const Text('Cancel'),
                          ),
                          TextButton(
                            onPressed: () => Navigator.pop(context, true),
                            style: TextButton.styleFrom(
                              foregroundColor: Colors.red,
                            ),
                            child: const Text('Logout'),
                          ),
                        ],
                      ),
                    );

                    if (confirmed == true) {
                      await authProvider.logout();
                    }
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.red,
                    foregroundColor: Colors.white,
                  ),
                  child: const Text('Logout'),
                ),
              ),
            ),
            const SizedBox(height: 16),
          ],
        ),
      ),
    );
  }
}
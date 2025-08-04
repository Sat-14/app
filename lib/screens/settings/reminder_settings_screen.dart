import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';
import '../../services/api_service.dart';
import '../../utils/helpers.dart';

class ReminderSettingsScreen extends StatefulWidget {
  const ReminderSettingsScreen({super.key});

  @override
  _ReminderSettingsScreenState createState() => _ReminderSettingsScreenState();
}

class _ReminderSettingsScreenState extends State<ReminderSettingsScreen> {
  bool _isLoading = true;
  bool _enableLocalNotifications = true;
  bool _enableWhatsApp = false;
  bool _enableCalls = false;
  int _daysBeforeReminder = 3;
  String _preferredTime = '09:00';

  @override
  void initState() {
    super.initState();
    _loadSettings();
  }

  Future<void> _loadSettings() async {
    try {
      final settings = await ApiService.getReminderSettings();
      setState(() {
        _enableLocalNotifications = settings['local_notifications'] ?? true;
        _enableWhatsApp = settings['whatsapp_enabled'] ?? false;
        _enableCalls = settings['call_enabled'] ?? false;
        _daysBeforeReminder = settings['days_before'] ?? 3;
        _preferredTime = settings['preferred_time'] ?? '09:00';
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
      });
      Helpers.showSnackBar(context, 'Failed to load settings', isError: true);
    }
  }

  Future<void> _saveSettings() async {
    setState(() {
      _isLoading = true;
    });

    try {
      await ApiService.updateReminderSettings({
        'local_notifications': _enableLocalNotifications,
        'whatsapp_enabled': _enableWhatsApp,
        'call_enabled': _enableCalls,
        'days_before': _daysBeforeReminder,
        'preferred_time': _preferredTime,
      });

      Helpers.showSnackBar(context, 'Settings saved successfully');
    } catch (e) {
      Helpers.showSnackBar(context, 'Failed to save settings', isError: true);
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  Future<void> _testReminder(String type) async {
    try {
      await ApiService.testReminder(type);
      Helpers.showSnackBar(context, 'Test $type sent successfully');
    } catch (e) {
      Helpers.showSnackBar(context, 'Failed to send test $type', isError: true);
    }
  }

  @override
  Widget build(BuildContext context) {
    final user = context.watch<AuthProvider>().user;
    final hasPhoneNumber = user?.phoneNumber != null && user!.phoneNumber!.isNotEmpty;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Reminder Settings'),
        actions: [
          if (!_isLoading)
            TextButton(
              onPressed: _saveSettings,
              child: const Text(
                'Save',
                style: TextStyle(color: Colors.white),
              ),
            ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Phone number status
                  if (!hasPhoneNumber)
                    Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: Colors.orange.withAlpha((0.1 * 255).toInt()),
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(
                          color: Colors.orange.withOpacity(0.3),
                        ),
                      ),
                      child: Row(
                        children: [
                          const Icon(Icons.warning, color: Colors.orange),
                          const SizedBox(width: 16),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  'Phone number required',
                                  style: TextStyle(
                                    fontWeight: FontWeight.bold,
                                    color: Colors.orange[900],
                                  ),
                                ),
                                const SizedBox(height: 4),
                                Text(
                                  'Add your phone number to enable WhatsApp and call reminders',
                                  style: TextStyle(
                                    fontSize: 12,
                                    color: Colors.orange[700],
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),
                  const SizedBox(height: 24),

                  // Reminder types
                  Text(
                    'REMINDER TYPES',
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                      color: Colors.grey[600],
                    ),
                  ),
                  const SizedBox(height: 16),

                  // Local notifications
                  Card(
                    child: SwitchListTile(
                      title: const Text('Push Notifications'),
                      subtitle: const Text('Get reminders on your device'),
                      secondary: const Icon(Icons.notifications),
                      value: _enableLocalNotifications,
                      onChanged: (value) {
                        setState(() {
                          _enableLocalNotifications = value;
                        });
                      },
                    ),
                  ),
                  const SizedBox(height: 8),

                  // WhatsApp
                  Card(
                    child: Column(
                      children: [
                        SwitchListTile(
                          title: const Text('WhatsApp Messages'),
                          subtitle: const Text('Receive reminders via WhatsApp'),
                          secondary: const Icon(Icons.message, color: Colors.green),
                          value: _enableWhatsApp && hasPhoneNumber,
                          onChanged: hasPhoneNumber
                              ? (value) {
                                  setState(() {
                                    _enableWhatsApp = value;
                                  });
                                }
                              : null,
                        ),
                        if (_enableWhatsApp && hasPhoneNumber)
                          Padding(
                            padding: const EdgeInsets.only(left: 72, right: 16, bottom: 16),
                            child: SizedBox(
                              width: double.infinity,
                              child: OutlinedButton(
                                onPressed: () => _testReminder('whatsapp'),
                                child: const Text('Send Test WhatsApp'),
                              ),
                            ),
                          ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 8),

                  // Calls
                  Card(
                    child: Column(
                      children: [
                        SwitchListTile(
                          title: const Text('Phone Calls'),
                          subtitle: const Text('Get reminder calls for urgent bills'),
                          secondary: const Icon(Icons.phone, color: Colors.blue),
                          value: _enableCalls && hasPhoneNumber,
                          onChanged: hasPhoneNumber
                              ? (value) {
                                  setState(() {
                                    _enableCalls = value;
                                  });
                                }
                              : null,
                        ),
                        if (_enableCalls && hasPhoneNumber)
                          Padding(
                            padding: const EdgeInsets.only(left: 72, right: 16, bottom: 16),
                            child: SizedBox(
                              width: double.infinity,
                              child: OutlinedButton(
                                onPressed: () => _testReminder('call'),
                                child: const Text('Send Test Call'),
                              ),
                            ),
                          ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 32),

                  // Timing settings
                  Text(
                    'TIMING SETTINGS',
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                      color: Colors.grey[600],
                    ),
                  ),
                  const SizedBox(height: 16),

                  // Days before
                  Card(
                    child: ListTile(
                      leading: const Icon(Icons.calendar_today),
                      title: const Text('Remind me'),
                      subtitle: Text('$_daysBeforeReminder days before due date'),
                      trailing: DropdownButton<int>(
                        value: _daysBeforeReminder,
                        items: [1, 2, 3, 5, 7].map((days) {
                          return DropdownMenuItem(
                            value: days,
                            child: Text('$days days'),
                          );
                        }).toList(),
                        onChanged: (value) {
                          setState(() {
                            _daysBeforeReminder = value!;
                          });
                        },
                      ),
                    ),
                  ),
                  const SizedBox(height: 8),

                  // Preferred time
                  Card(
                    child: ListTile(
                      leading: const Icon(Icons.access_time),
                      title: const Text('Preferred time'),
                      subtitle: Text('Send reminders at $_preferredTime'),
                      onTap: () async {
                        final time = await showTimePicker(
                          context: context,
                          initialTime: TimeOfDay(
                            hour: int.parse(_preferredTime.split(':')[0]),
                            minute: int.parse(_preferredTime.split(':')[1]),
                          ),
                        );
                        if (time != null) {
                          setState(() {
                            _preferredTime = '${time.hour.toString().padLeft(2, '0')}:${time.minute.toString().padLeft(2, '0')}';
                          });
                        }
                      },
                    ),
                  ),

                  const SizedBox(height: 32),

                  // Info
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Colors.blue.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Icon(Icons.info, color: Colors.blue, size: 20),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Text(
                            'WhatsApp and call reminders will be sent to ${user?.phoneNumber ?? "your phone number"}. Standard messaging rates may apply.',
                            style: TextStyle(
                              fontSize: 14,
                              color: Colors.blue[700],
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
    );
  }
}
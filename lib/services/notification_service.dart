import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:timezone/timezone.dart' as tz;
import 'package:timezone/data/latest.dart' as tz;
import '../models/bill.dart';

class NotificationService {
  static final FlutterLocalNotificationsPlugin _notifications = FlutterLocalNotificationsPlugin();

  static Future<void> initialize() async {
    tz.initializeTimeZones();

    const androidSettings = AndroidInitializationSettings('@mipmap/ic_launcher');
    const iosSettings = DarwinInitializationSettings(
      requestSoundPermission: true,
      requestBadgePermission: true,
      requestAlertPermission: true,
    );

    const initSettings = InitializationSettings(
      android: androidSettings,
      iOS: iosSettings,
    );

    await _notifications.initialize(
      initSettings,
      onDidReceiveNotificationResponse: _onNotificationTapped,
    );
  }

  static void _onNotificationTapped(NotificationResponse response) {
    // Handle notification tap if needed
  }

  static Future<void> scheduleAllBillReminders(Bill bill) async {
    await scheduleBillReminder(bill, 3);
    await scheduleBillReminder(bill, 1);
    await scheduleBillReminder(bill, 0);
  }

  static Future<void> scheduleBillReminder(Bill bill, int daysBefore) async {
    final scheduledDate = bill.dueDate.subtract(Duration(days: daysBefore));

    if (scheduledDate.isAfter(DateTime.now())) {
      const androidDetails = AndroidNotificationDetails(
        'bill_reminders',
        'Bill Reminders',
        channelDescription: 'Notifications for upcoming bill payments',
        importance: Importance.high,
        priority: Priority.high,
      );

      const iosDetails = DarwinNotificationDetails();

      const details = NotificationDetails(
        android: androidDetails,
        iOS: iosDetails,
      );

      await _notifications.zonedSchedule(
        bill.id.hashCode + daysBefore,
        'Bill Due Soon',
        '${bill.name} - \$${bill.amount.toStringAsFixed(2)} due in $daysBefore day(s)',
        tz.TZDateTime.from(scheduledDate, tz.local),
        details,
        uiLocalNotificationDateInterpretation: UILocalNotificationDateInterpretation.absoluteTime,
        androidScheduleMode: AndroidScheduleMode.exactAllowWhileIdle,
        payload: bill.id,
      );
    }
  }

  static Future<void> cancelBillReminders(String billId) async {
    await cancelNotification(billId.hashCode + 3);
    await cancelNotification(billId.hashCode + 1);
    await cancelNotification(billId.hashCode + 0);
  }

  static Future<void> showInstantNotification(String title, String body) async {
    const androidDetails = AndroidNotificationDetails(
      'instant_notifications',
      'Instant Notifications',
      channelDescription: 'Instant notifications for app events',
      importance: Importance.high,
      priority: Priority.high,
    );

    const iosDetails = DarwinNotificationDetails();

    const details = NotificationDetails(
      android: androidDetails,
      iOS: iosDetails,
    );

    await _notifications.show(
      DateTime.now().millisecondsSinceEpoch.remainder(100000),
      title,
      body,
      details,
    );
  }

  static Future<void> cancelNotification(int id) async {
    await _notifications.cancel(id);
  }

  static Future<void> cancelAllNotifications() async {
    await _notifications.cancelAll();
  }
}

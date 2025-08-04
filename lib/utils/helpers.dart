import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../models/bill.dart';

class Helpers {
  // Date formatting
  static String formatDate(DateTime date) {
    return DateFormat('MMM dd, yyyy').format(date);
  }

  static String formatDateShort(DateTime date) {
    return DateFormat('MMM dd').format(date);
  }

  static String formatCurrency(double amount) {
    return '\$${amount.toStringAsFixed(2)}';
  }

  static String getDaysUntilDue(DateTime dueDate) {
    final now = DateTime.now();
    final difference = dueDate.difference(now).inDays;
    
    if (difference < 0) {
      return '${-difference} days overdue';
    } else if (difference == 0) {
      return 'Due today';
    } else if (difference == 1) {
      return 'Due tomorrow';
    } else {
      return 'Due in $difference days';
    }
  }

  static Color getBillStatusColor(Bill bill) {
    if (bill.isPaid) {
      return Colors.green;
    }
    
    final now = DateTime.now();
    final daysUntilDue = bill.dueDate.difference(now).inDays;
    
    if (daysUntilDue < 0) {
      return Colors.red;
    } else if (daysUntilDue <= 3) {
      return Colors.orange;
    } else {
      return Colors.blue;
    }
  }

  static String getCategoryEmoji(BillCategory category) {
    final categoryName = category.toString().split('.').last;
    return {
      'utilities': '💡',
      'rent': '🏠',
      'insurance': '🛡️',
      'subscription': '📱',
      'other': '📄',
    }[categoryName] ?? '📄';
  }

  static String getFrequencyLabel(BillFrequency frequency) {
    final frequencyName = frequency.toString().split('.').last;
    return {
      'once': 'One Time',
      'weekly': 'Weekly',
      'monthly': 'Monthly',
      'quarterly': 'Quarterly',
      'yearly': 'Yearly',
    }[frequencyName] ?? 'Monthly';
  }

  static DateTime getNextDueDate(Bill bill) {
    if (bill.frequency == BillFrequency.once || !bill.isPaid) {
      return bill.dueDate;
    }

    DateTime nextDate = bill.dueDate;
    final now = DateTime.now();

    while (nextDate.isBefore(now)) {
      switch (bill.frequency) {
        case BillFrequency.weekly:
          nextDate = nextDate.add(const Duration(days: 7));
          break;
        case BillFrequency.monthly:
          nextDate = DateTime(
            nextDate.year,
            nextDate.month + 1,
            nextDate.day,
          );
          break;
        case BillFrequency.quarterly:
          nextDate = DateTime(
            nextDate.year,
            nextDate.month + 3,
            nextDate.day,
          );
          break;
        case BillFrequency.yearly:
          nextDate = DateTime(
            nextDate.year + 1,
            nextDate.month,
            nextDate.day,
          );
          break;
        default:
          break;
      }
    }

    return nextDate;
  }

  static void showSnackBar(BuildContext context, String message, {bool isError = false}) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: isError ? Colors.red : Colors.green,
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
        ),
      ),
    );
  }

  static Future<bool> showConfirmDialog(
    BuildContext context, {
    required String title,
    required String content,
    String confirmText = 'Confirm',
    String cancelText = 'Cancel',
  }) async {
    final result = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(title),
        content: Text(content),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: Text(cancelText),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            style: TextButton.styleFrom(
              foregroundColor: Colors.red,
            ),
            child: Text(confirmText),
          ),
        ],
      ),
    );

    return result ?? false;
  }
}
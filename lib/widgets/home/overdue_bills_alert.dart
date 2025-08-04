import 'package:flutter/material.dart';
import '../../models/bill.dart';
import '../../utils/helpers.dart';

class OverdueBillsAlert extends StatelessWidget {
  final List<Bill> bills;

  const OverdueBillsAlert({super.key, required this.bills});

  @override
  Widget build(BuildContext context) {
    final totalOverdue = bills.fold(
      0.0,
      (sum, bill) => sum + bill.amount,
    );

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.red.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: Colors.red.withOpacity(0.3),
          width: 1,
        ),
      ),
      child: Row(
        children: [
          const Icon(
            Icons.warning_rounded,
            color: Colors.red,
            size: 32,
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '${bills.length} Overdue Bill${bills.length > 1 ? 's' : ''}',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: Colors.red[900],
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  'Total: ${Helpers.formatCurrency(totalOverdue)}',
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.red[700],
                  ),
                ),
              ],
            ),
          ),
          TextButton(
            onPressed: () {
              // Navigate to bills list with overdue filter
            },
            child: const Text(
              'View',
              style: TextStyle(
                color: Colors.red,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
import 'package:flutter/material.dart';
import '../../models/bill.dart';
import '../../utils/helpers.dart';
import '../../config/theme.dart';

class UpcomingBillCard extends StatelessWidget {
  final Bill bill;

  const UpcomingBillCard({super.key, required this.bill});

  @override
  Widget build(BuildContext context) {
    final daysUntilDue = bill.dueDate.difference(DateTime.now()).inDays;
    final statusColor = Helpers.getBillStatusColor(bill);

    return Card(
      child: InkWell(
        onTap: () {
          // Navigate to bill details
        },
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              Container(
                width: 48,
                height: 48,
                decoration: BoxDecoration(
                  color: AppTheme
                      .categoryColors[bill.category.toString().split('.').last]
                      ?.withAlpha(51),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Center(
                  child: Text(
                    Helpers.getCategoryEmoji(bill.category),
                    style: const TextStyle(fontSize: 24),
                  ),
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      bill.name,
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      Helpers.getDaysUntilDue(bill.dueDate),
                      style: TextStyle(
                        fontSize: 14,
                        color: statusColor,
                      ),
                    ),
                  ],
                ),
              ),
              Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Text(
                    Helpers.formatCurrency(bill.amount),
                    style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                    decoration: BoxDecoration(
                      color: statusColor.withOpacity(0.2),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      daysUntilDue <= 0 ? 'Overdue' : '$daysUntilDue days',
                      style: TextStyle(
                        fontSize: 12,
                        color: statusColor,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

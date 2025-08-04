import 'package:flutter/material.dart';
import '../../models/bill.dart';
import '../../utils/helpers.dart';
import '../../config/theme.dart';
import 'package:final_wali_file/extensions/string_extensions.dart';


class MonthlySummaryChart extends StatelessWidget {
  final double totalAmount;
  final Map<BillCategory, double> categoryBreakdown;

  const MonthlySummaryChart({
    super.key,
    required this.totalAmount,
    required this.categoryBreakdown,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Total Due',
                      style: TextStyle(
                        fontSize: 14,
                        color: Colors.grey[600],
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      Helpers.formatCurrency(totalAmount),
                      style: const TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
                Icon(
                  Icons.pie_chart,
                  size: 48,
                  color: Theme.of(context).primaryColor.withAlpha((0.3 * 255).round()),

                ),
              ],
            ),
            const SizedBox(height: 20),
            Text(
              'By Category',
              style: TextStyle(
                fontSize: 12,
                color: Colors.grey[600],
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            ...categoryBreakdown.entries.map((entry) {
              final percentage = totalAmount > 0
                  ? (entry.value / totalAmount * 100).toStringAsFixed(0)
                  : '0';
              final categoryName = entry.key.toString().split('.').last;
              final color = AppTheme.categoryColors[categoryName]!;

              return Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: Row(
                  children: [
                    Container(
                      width: 12,
                      height: 12,
                      decoration: BoxDecoration(
                        color: color,
                        borderRadius: BorderRadius.circular(3),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        categoryName.capitalize(),
                        style: const TextStyle(fontSize: 14),
                      ),
                    ),
                    Text(
                      '$percentage%',
                      style: const TextStyle(
                        fontSize: 14,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(width: 8),
                    Text(
                      Helpers.formatCurrency(entry.value),
                      style: TextStyle(
                        fontSize: 14,
                        color: Colors.grey[600],
                      ),
                    ),
                  ],
                ),
              );
            }),
          ],
        ),
      ),
    );
  }
}


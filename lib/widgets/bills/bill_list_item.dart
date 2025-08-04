import 'package:flutter/material.dart';
import 'package:flutter_slidable/flutter_slidable.dart';
import '../../models/bill.dart';
import '../../utils/helpers.dart';
import '../../config/theme.dart';

class BillListItem extends StatelessWidget {
  final Bill bill;
  final VoidCallback onTap;
  final VoidCallback onDelete;
  final VoidCallback onMarkPaid;

  const BillListItem({
    super.key,
    required this.bill,
    required this.onTap,
    required this.onDelete,
    required this.onMarkPaid,
  });

  @override
  Widget build(BuildContext context) {
    final categoryName = bill.category.toString().split('.').last;
    final categoryColor = AppTheme.categoryColors[categoryName]!;
    final statusColor = Helpers.getBillStatusColor(bill);

    return Slidable(
      endActionPane: ActionPane(
        motion: const ScrollMotion(),
        children: [
          if (!bill.isPaid)
            SlidableAction(
              onPressed: (_) => onMarkPaid(),
              backgroundColor: Colors.green,
              foregroundColor: Colors.white,
              icon: Icons.check,
              label: 'Paid',
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(12),
                bottomLeft: Radius.circular(12),
              ),
            ),
          SlidableAction(
            onPressed: (_) => onDelete(),
            backgroundColor: Colors.red,
            foregroundColor: Colors.white,
            icon: Icons.delete,
            label: 'Delete',
            borderRadius: BorderRadius.only(
              topRight: const Radius.circular(12),
              bottomRight: const Radius.circular(12),
              topLeft: bill.isPaid ? const Radius.circular(12) : Radius.zero,
              bottomLeft: bill.isPaid ? const Radius.circular(12) : Radius.zero,
            ),
          ),
        ],
      ),
      child: Card(
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(12),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                Container(
                  width: 48,
                  height: 48,
                  decoration: BoxDecoration(
                    color: categoryColor.withOpacity(0.2),
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
                      Row(
                        children: [
                          Expanded(
                            child: Text(
                              bill.name,
                              style: TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.bold,
                                decoration: bill.isPaid
                                    ? TextDecoration.lineThrough
                                    : null,
                              ),
                            ),
                          ),
                          if (bill.isPaid)
                            Container(
                              padding: const EdgeInsets.symmetric(
                                horizontal: 8,
                                vertical: 2,
                              ),
                              decoration: BoxDecoration(
                                color: Colors.green.withOpacity(0.2),
                                borderRadius: BorderRadius.circular(12),
                              ),
                              child: const Text(
                                'PAID',
                                style: TextStyle(
                                  fontSize: 10,
                                  color: Colors.green,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ),
                        ],
                      ),
                      const SizedBox(height: 4),
                      Row(
                        children: [
                          Icon(
                            Icons.calendar_today,
                            size: 14,
                            color: Colors.grey[600],
                          ),
                          const SizedBox(width: 4),
                          Text(
                            Helpers.formatDate(bill.dueDate),
                            style: TextStyle(
                              fontSize: 14,
                              color: Colors.grey[600],
                            ),
                          ),
                          const SizedBox(width: 16),
                          Icon(
                            Icons.repeat,
                            size: 14,
                            color: Colors.grey[600],
                          ),
                          const SizedBox(width: 4),
                          Text(
                            Helpers.getFrequencyLabel(bill.frequency),
                            style: TextStyle(
                              fontSize: 14,
                              color: Colors.grey[600],
                            ),
                          ),
                        ],
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
                    if (!bill.isPaid)
                      Text(
                        Helpers.getDaysUntilDue(bill.dueDate),
                        style: TextStyle(
                          fontSize: 12,
                          color: statusColor,
                        ),
                      ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
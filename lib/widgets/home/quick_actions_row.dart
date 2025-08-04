import 'package:flutter/material.dart';

class QuickActionsRow extends StatelessWidget {
  final VoidCallback onAddBill;
  final VoidCallback onViewReports;

  const QuickActionsRow({
    super.key,
    required this.onAddBill,
    required this.onViewReports,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Expanded(
          child: _QuickActionCard(
            icon: Icons.add_circle,
            label: 'Add Bill',
            color: Theme.of(context).primaryColor,
            onTap: onAddBill,
          ),
        ),
        const SizedBox(width: 16),
        Expanded(
          child: _QuickActionCard(
            icon: Icons.analytics,
            label: 'View Reports',
            color: Colors.orange,
            onTap: onViewReports,
          ),
        ),
      ],
    );
  }
}

class _QuickActionCard extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color color;
  final VoidCallback onTap;

  const _QuickActionCard({
    required this.icon,
    required this.label,
    required this.color,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              Container(
                width: 40,
                height: 40,
                decoration: BoxDecoration(
                  color: color.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(
                  icon,
                  color: color,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  label,
                  style: const TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}